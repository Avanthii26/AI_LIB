"""LibAI: simulated university library discovery, circulation, and route planning."""
import pandas as pd
import streamlit as st
from library_data import BOOKS, GRID_SIZE, ENTRANCE, OBSTACLES, get_categories
from semantic_search import SemanticSearch
from astar import astar, path_length
from hill_climbing import hill_climbing, route_cost, exhaustive_best_order

st.set_page_config(page_title="LibAI | University Library", page_icon="📚", layout="wide")
st.markdown("""
<style>
.stApp { background: #0b1424; color: #f3f6fb; }
[data-testid="stSidebar"] { background: #111f35; border-right: 1px solid #283b56; }
[data-testid="stSidebar"] * { color: #eef4ff !important; }
.stApp p, .stApp label, .stApp span { color: #e5edf8; }
[data-testid="stMetric"] { background: #14243a; border: 1px solid #2b405d; padding: 14px; border-radius: 12px; }
[data-testid="stMetricValue"] { color: #ffffff; }
.book-card { background: #13243a; border: 1px solid #2b405d; padding: 16px; border-radius: 12px; margin: 8px 0; }
.book-title { font-size: 1.04rem; font-weight: 700; color: #ffffff; }
.muted { color: #b8c7da !important; font-size: .88rem; }
.library-banner { padding: 26px; border-radius: 18px; background: linear-gradient(120deg,#173653,#17243b 70%,#2b3c53); border: 1px solid #3b526d; margin-bottom: 16px; }
.pill { padding: 4px 9px; border-radius: 20px; font-size: .8rem; font-weight: 700; }
div.stButton > button { border-radius: 9px; }

   div.st-key-signout_btn button {
       background-color: #dc2626 !important;
       color: white !important;
       border: none !important;
       border-radius: 8px !important;
   }

   div.st-key-signout_btn button:hover {
       background-color: #b91c1c !important;
       color: white !important;
   }
   
/* Add to route buttons only */
div[class*="st-key-add_route_btn_"] button {
    background-color: #2563eb !important;
    color: #ffffff !important;
    border: 1px solid #3b82f6 !important;
    border-radius: 8px !important;
}

div[class*="st-key-add_route_btn_"] button:hover {
    background-color: #1d4ed8 !important;
    color: #ffffff !important;
}  
</style>
""", unsafe_allow_html=True)

if "auth_user" not in st.session_state:
    st.session_state.auth_user = None
if "auth_role" not in st.session_state:
    st.session_state.auth_role = None
if "registered_students" not in st.session_state:
    st.session_state.registered_students = {"student": "student123"}

def login_screen():
    st.markdown("<div class='library-banner'><div style='font-size:2rem;font-weight:800'>LIBAI <span style='color:#9bc8ff'>PORTAL</span></div><div style='font-size:1.05rem;margin-top:8px'>University Library Management & Discovery</div><div style='color:#bfd0e4;margin-top:8px'>Sign in to access student services or library administration.</div></div>", unsafe_allow_html=True)
    left, right = st.columns([1.1, 1])
    with left:
        st.subheader("Sign in")
        role = st.radio("I am signing in as", ["Student", "Administrator"], horizontal=True)
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        if st.button("Sign in", type="primary", use_container_width=True):
            valid = (role == "Administrator" and username == "admin" and password == "admin123") or (role == "Student" and st.session_state.registered_students.get(username) == password)
            if valid:
                st.session_state.auth_user = username
                st.session_state.auth_role = "admin" if role == "Administrator" else "student"
                st.rerun()
            else:
                st.error("Invalid username or password.")
    with right:
        st.subheader("Library portal access")
        st.markdown("**Student services**")
        st.write("Discover books, check copy availability, borrow and return titles, receive recommendations, and plan shelf routes.")
        st.markdown("**Administrator services**")
        st.write("Review circulation metrics, manage copy counts, inspect the catalog, and view demo loan activity.")
        st.info("Demo administrator: `admin` / `admin123`\n\nDemo student: `student` / `student123`", icon="🔐")
        st.caption("Demonstration authentication only. Do not use these credentials for a real library deployment.")

if st.session_state.auth_user is None:
    login_screen()
    st.stop()

if "selected_books" not in st.session_state: st.session_state.selected_books = []
if "last_query" not in st.session_state: st.session_state.last_query = ""
if "home_results" not in st.session_state: st.session_state.home_results = []
if "search_results" not in st.session_state: st.session_state.search_results = []
if "session_borrowed" not in st.session_state: st.session_state.session_borrowed = []
if "inventory" not in st.session_state:
    st.session_state.inventory = {b["id"]: {"available": b["available_copies"], "total": b["total_copies"], "baseline_borrowed": b["borrowed_copies"]} for b in BOOKS}

@st.cache_resource
def get_search_engine():
    return SemanticSearch(BOOKS)
engine = get_search_engine()
book_by_id = {b["id"]: b for b in BOOKS}

def inventory(book):
    return st.session_state.inventory[book["id"]]

def availability_label(book):
    inv = inventory(book)
    if inv["available"] <= 0: return "Borrowed / Unavailable"
    if inv["available"] < inv["total"]: return "Limited availability"
    return "Available"

def availability_color(label):
    return {"Available":"#4ade80", "Limited availability":"#fbbf24", "Borrowed / Unavailable":"#fb7185"}.get(label,"#cbd5e1")

def add_to_route(book):
    if book["id"] not in st.session_state.selected_books:
        st.session_state.selected_books.append(book["id"])

def selected_book_objects():
    return [book_by_id[bid] for bid in st.session_state.selected_books if bid in book_by_id]

def distance_fn(a, b):
    return path_length(astar(a, b, grid_size=GRID_SIZE, obstacles=OBSTACLES))

def get_complete_route(order):
    full_path, segments, current = [], [], ENTRANCE
    for target in order:
        segment = astar(current, target, grid_size=GRID_SIZE, obstacles=OBSTACLES)
        if not segment: return None, segments
        full_path.extend(segment if not full_path else segment[1:])
        segments.append(segment); current = target
    return full_path, segments

def render_grid(path=None, chosen_positions=None):
    path_set, chosen_positions = set(path or []), set(chosen_positions or [])
    rows=[]
    for r in range(GRID_SIZE):
        row=[]
        for c in range(GRID_SIZE):
            p=(r,c)
            if p == ENTRANCE: cell="🚪"
            elif p in chosen_positions: cell="📚"
            elif p in OBSTACLES: cell="🟥"
            elif p in path_set: cell="🟦"
            else: cell="·"
            row.append(cell)
        rows.append(row)
    st.dataframe(pd.DataFrame(rows, columns=[str(i) for i in range(GRID_SIZE)]), use_container_width=True, hide_index=True, height=360)
    st.caption("🚪 Entrance · 📚 Selected shelf access point · 🟥 Shelf / blocked cell · 🟦 Route · · Walkable aisle")

def book_card(book, key_prefix="book", show_route=True):
    label=availability_label(book); inv=inventory(book)
    with st.container(border=True):
        left, right = st.columns([5,1])
        with left:
            st.markdown(f"**{book['title']}**")
            st.caption(f"{book['author']} · {book['category']} · Shelf {book['shelf']} · {book['publication_year']}")
            st.write(book['description'])
            st.caption(f"ISBN: {book['isbn']} · Language: {book['language']} · Loan period: {book['loan_period_days']} days")
        with right:
            st.markdown(f"<span style='color:{availability_color(label)};font-weight:700'>{label}</span>", unsafe_allow_html=True)
            st.metric("Available", f"{inv['available']} / {inv['total']}")

        

    buttons = st.columns(2 if show_route else 1)

    with buttons[0].container(key=f"add_route_btn_{key_prefix}_{book['id']}"):        
        if show_route and st.button(
            "＋ Add to route",
            key=f"{key_prefix}_route_{book['id']}",
            use_container_width=True
        ):
            add_to_route(book)
            st.success("Added to navigation route.")

    if show_route:
        target = buttons[1]
    else:
        target = buttons[0]

    if inv["available"] > 0:
        if target.button(
            "Borrow copy",
            key=f"{key_prefix}_borrow_{book['id']}",
            use_container_width=True
        ):
            inv["available"] -= 1
            st.session_state.session_borrowed.append(book["id"])
            st.success(f"Demo checkout recorded for '{book['title']}'.")
            st.rerun()
    else:
        target.button(
            "Currently unavailable",
            key=f"{key_prefix}_unavailable_{book['id']}",
            disabled=True,
            use_container_width=True
        )
st.sidebar.markdown("# 📚 LibAI")
st.sidebar.caption("UNIVERSITY LIBRARY · ROLE-BASED PORTAL")
st.sidebar.markdown(f"**Signed in:** {st.session_state.auth_user}")
st.sidebar.caption("Administrator" if st.session_state.auth_role == "admin" else "Student account")
if st.session_state.auth_role == "admin":
    pages = ["Admin Dashboard", "Manage Inventory", "Circulation Records", "Library Catalog", "Library Insights"]
else:
    pages = ["Home", "Discover Books", "Library Catalog", "Borrow & Return", "AI Navigation", "Library Insights"]
page=st.sidebar.radio("Library services", pages)
with st.sidebar.container(key="signout_btn"):
    if st.button("Sign out", use_container_width=True):
        st.session_state.auth_user = None
        st.session_state.auth_role = None
        st.rerun()
st.sidebar.divider()
available_total=sum(inventory(b)["available"] for b in BOOKS)
st.sidebar.metric("Catalog titles",len(BOOKS))
st.sidebar.metric("Copies available",available_total)
st.sidebar.metric("Active demo loans",len(st.session_state.session_borrowed))
if st.sidebar.button("Clear selected route", use_container_width=True):
    st.session_state.selected_books=[]; st.rerun()
st.sidebar.caption(f"Search engine: {engine.backend}")

if page == "Admin Dashboard":
    st.title("🛡️ Administrator Dashboard")
    st.caption("Library operations overview · simulated inventory")
    total_copies = sum(inventory(x)["total"] for x in BOOKS)
    available = sum(inventory(x)["available"] for x in BOOKS)
    borrowed = total_copies - available
    a,b,c,d = st.columns(4)
    a.metric("Catalog titles", len(BOOKS)); b.metric("Physical copies", total_copies)
    c.metric("Available copies", available); d.metric("Borrowed / unavailable", borrowed)
    st.subheader("Inventory status")
    status_rows = []
    for bk in BOOKS:
        inv = inventory(bk)
        status_rows.append({"Title":bk["title"], "Author":bk["author"], "Category":bk["category"], "Shelf":bk["shelf"], "Available":inv["available"], "Total":inv["total"], "Status":availability_label(bk)})
    st.dataframe(pd.DataFrame(status_rows), use_container_width=True, hide_index=True)
    st.subheader("Quick actions")
    st.write("Use **Manage Inventory** to adjust copy counts and **Circulation Records** to review demo loans.")
    st.warning("This demo uses in-session inventory. Changes reset when the Streamlit session/server state is reset; add a database before real deployment.")

elif page == "Manage Inventory":
    st.title("📦 Manage Inventory")
    st.write("Administrators can update copy counts and availability for existing catalog titles.")
    choices = {f"{bk['title']} — {bk['shelf']} ({bk['id']})": bk for bk in BOOKS}
    chosen_label = st.selectbox("Select a book", list(choices.keys()))
    bk = choices[chosen_label]; inv = inventory(bk)
    st.markdown(f"### {bk['title']}")
    st.caption(f"{bk['author']} · {bk['category']} · ISBN {bk['isbn']}")
    st.write(f"Current availability: **{inv['available']} available of {inv['total']} copies**")
    with st.form("inventory_update_form"):
        new_total = st.number_input("Total physical copies", min_value=1, max_value=500, value=int(inv["total"]), step=1)
        new_available = st.number_input("Available copies", min_value=0, max_value=int(new_total), value=min(int(inv["available"]), int(new_total)), step=1)
        submitted = st.form_submit_button("Save inventory", type="primary")
        if submitted:
            if new_available > new_total:
                st.error("Available copies cannot exceed total copies.")
            else:
                inv["total"] = int(new_total); inv["available"] = int(new_available)
                st.success("Inventory updated for this session.")
                st.rerun()
    st.subheader("Inventory needing attention")
    low = [x for x in BOOKS if inventory(x)["available"] == 0 or inventory(x)["available"] < inventory(x)["total"]]
    if low:
        st.dataframe(pd.DataFrame([{"Title":x["title"],"Shelf":x["shelf"],"Available":inventory(x)["available"],"Total":inventory(x)["total"],"Status":availability_label(x)} for x in low]), use_container_width=True, hide_index=True)
    else: st.success("All catalog titles have every copy available.")

elif page == "Circulation Records":
    st.title("🧾 Circulation Records")
    st.caption("Demo circulation activity visible to library administrators.")
    if st.session_state.session_borrowed:
        rows=[]
        for i,bid in enumerate(st.session_state.session_borrowed,1):
            bk=book_by_id[bid]
            rows.append({"Record":i,"Borrower":"Demo student session","Book":bk["title"],"ISBN":bk["isbn"],"Shelf":bk["shelf"],"Loan period (days)":bk["loan_period_days"],"Status":"Borrowed"})
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info("No active demo loans recorded in this session yet.")
    if st.button("Refresh circulation view"):
        st.rerun()
    st.warning("For privacy and persistence, real circulation records should be stored in a database with individual student accounts and timestamps.")

if page == "Home":
    st.markdown("<div class='library-banner'><div style='font-size:2rem;font-weight:800'>LIBAI <span style='color:#9bc8ff'>UNIVERSITY LIBRARY</span></div><div style='font-size:1.05rem;margin-top:8px'>Discover knowledge. Check availability. Plan your library visit.</div><div style='color:#bfd0e4;margin-top:8px'>A smart library portal with catalog search, simulated circulation, recommendations and aisle-aware navigation.</div></div>",unsafe_allow_html=True)
    c1,c2,c3,c4=st.columns(4)
    c1.metric("Catalog titles",len(BOOKS)); c2.metric("Available copies",available_total); c3.metric("Subject areas",len(get_categories())); c4.metric("Books borrowed in demo",len(st.session_state.session_borrowed))
    st.subheader("Search the library")
    q=st.text_input("Search by topic, title, or learning goal",placeholder="e.g. books to learn computer vision")
    if st.button("Search library",type="primary") and q.strip():
        st.session_state.last_query=q; st.session_state.home_results=engine.search(q,top_k=6)
    for b in st.session_state.home_results: book_card(b,"home")
    st.subheader("Browse by subject")
    cols=st.columns(4)
    for i,cat in enumerate(get_categories()):
        count=sum(b['category']==cat for b in BOOKS)
        cols[i%4].markdown(f"<div class='book-card'><b>{cat}</b><div class='muted'>{count} title(s)</div></div>",unsafe_allow_html=True)

elif page == "Discover Books":
    st.title("🔎 Discover Books")
    query=st.text_input("Describe what you want to learn",value=st.session_state.last_query,placeholder="e.g. understand encryption and digital signatures")
    c1,c2,c3=st.columns(3)
    category=c1.selectbox("Subject",["All subjects"]+get_categories())
    author=c2.selectbox("Author",["All authors"]+sorted({b['author'] for b in BOOKS}))
    status=c3.selectbox("Availability",["Any status","Available","Limited availability","Borrowed / Unavailable"])
    if st.button("Search catalog",type="primary"):
        st.session_state.last_query=query
        results=engine.search(query,top_k=len(BOOKS) or 1,category=None if category=="All subjects" else category,author=None if author=="All authors" else author)
        st.session_state.search_results=[b for b in results if status=="Any status" or availability_label(b)==status][:20]
    results=st.session_state.search_results
    st.caption(f"{len(results)} result(s) · relevance ranking uses {engine.backend}. Availability is simulated demo inventory.")
    for b in results: book_card(b,"discover")
    if results:
        st.subheader("Recommended for you")
        seed=st.selectbox("Choose a title for related recommendations",results,format_func=lambda b:b['title'],key="recommendation_seed")
        for b in engine.recommend_books(seed,top_k=4): book_card(b,"recommendation")
    elif query: st.info("Run a search to see results, or change your filters.")

elif page == "Library Catalog":
    st.title("📖 Library Catalog & Availability")
    st.write("Browse the library's simulated inventory, including shelf location, publication information, and current copy availability.")
    c1,c2,c3=st.columns([2,1,1])
    query=c1.text_input("Title, author, ISBN, or keyword")
    category=c2.selectbox("Subject",["All subjects"]+get_categories())
    status=c3.selectbox("Availability",["All statuses","Available","Limited availability","Borrowed / Unavailable"])
    filtered=[]
    for b in BOOKS:
        text=f"{b['title']} {b['author']} {b['description']} {b['isbn']} {b['shelf']}".lower()
        if query.lower() not in text: continue
        if category!="All subjects" and b['category']!=category: continue
        if status!="All statuses" and availability_label(b)!=status: continue
        filtered.append(b)
    st.caption(f"Showing {len(filtered)} of {len(BOOKS)} catalog titles")
    if filtered:
        for b in filtered: book_card(b,"catalog")
    else: st.info("No titles match those filters.")

elif page == "Borrow & Return":
    st.title("🪪 Library Circulation Desk")
    st.warning("This is a local demonstration. Checkout and return changes are stored in the current Streamlit session only; they are not connected to a real library database.")
    c1,c2,c3=st.columns(3)
    c1.metric("Titles in catalog",len(BOOKS)); c2.metric("Copies available",available_total); c3.metric("Your active demo loans",len(st.session_state.session_borrowed))
    st.subheader("Borrow a book")
    query=st.text_input("Find a title to borrow",key="borrow_query")
    matches=[b for b in BOOKS if query.lower() in f"{b['title']} {b['author']} {b['category']}".lower()]
    matches=matches[:12]
    if matches:
        for b in matches: book_card(b,"circulation",show_route=False)
    else: st.caption("Enter a title, author, or subject to find a copy.")
    st.subheader("Your current demo loans")
    if not st.session_state.session_borrowed:
        st.info("You have no active demo loans. Borrow an available copy above to see it here.")
    else:
        for idx,bid in enumerate(list(st.session_state.session_borrowed)):
            b=book_by_id[bid]
            with st.container(border=True):
                left,right=st.columns([5,1])
                left.write(f"**{b['title']}**")
                left.caption(f"Shelf {b['shelf']} · Standard loan period: {b['loan_period_days']} days · Demo loan")
                if right.button("Return",key=f"return_{idx}_{bid}"):
                    inventory(b)["available"] += 1
                    st.session_state.session_borrowed.remove(bid)
                    st.success("Return recorded."); st.rerun()

elif page == "AI Navigation":
    st.title("🧭 Library Navigation & Route Optimization")
    selected=selected_book_objects()
    if not selected: st.info("No books selected. Add titles from Discover Books or the Library Catalog.")
    else:
        st.caption("Route planning is based on shelf access coordinates in the simulated library map.")
        for b in selected:
            col1,col2,col3=st.columns([5,2,1])
            col1.write(f"**{b['title']}**"); col2.caption(f"Shelf {b['shelf']} · {b['position']}")
            if col3.button("Remove",key=f"remove_{b['id']}"): st.session_state.selected_books.remove(b['id']); st.rerun()
        positions=[tuple(b['position']) for b in selected]
        original=positions[:]
        optimized=hill_climbing(positions,entrance=ENTRANCE,distance_fn=distance_fn)
        original_cost=route_cost(original,ENTRANCE,distance_fn)
        optimized_cost=route_cost(optimized,ENTRANCE,distance_fn)
        route,segments=get_complete_route(optimized)
        def display_cost(v): return "Unreachable" if v is None or v==float('inf') else f"{int(v)} steps"
        a,b,c=st.columns(3); a.metric("Original selection",display_cost(original_cost)); b.metric("Hill Climbing",display_cost(optimized_cost))
        if original_cost not in (0,float('inf'),None) and optimized_cost not in (float('inf'),None):
            pct=(original_cost-optimized_cost)/original_cost*100; c.metric("Distance reduction",f"{pct:.1f}%")
        else: c.metric("Distance reduction","N/A")
        compare=pd.DataFrame([{"Method":"Original selection order","Distance (steps)":None if original_cost==float('inf') else original_cost},{"Method":"Hill Climbing","Distance (steps)":None if optimized_cost==float('inf') else optimized_cost}])
        st.bar_chart(compare.set_index("Method"))
        if len(positions)<=8:
            best,best_cost=exhaustive_best_order(positions,ENTRANCE,distance_fn=distance_fn,max_books=8)
            if best is not None and best_cost!=float('inf'): st.info(f"Small-case exhaustive benchmark: {int(best_cost)} steps. It checks every ordering and is intended only for small selections.")
        st.subheader("Recommended collection order")
        by_position={tuple(x['position']):x for x in selected}
        for i,pos in enumerate(optimized,1):
            bk=by_position.get(pos)
            if bk: st.write(f"{i}. **{bk['title']}** — Shelf {bk['shelf']} · {pos} · {availability_label(bk)}")
        st.subheader("Library floor grid")
        if route is None: st.error("A complete route could not be generated. Review shelf positions and obstacles.")
        else: render_grid(route,positions); st.success(f"Complete route: {path_length(route)} movement steps.")
        with st.expander("Route segment details"):
            for i,seg in enumerate(segments,1): st.write(f"Segment {i}: {seg[0]} → {seg[-1]} · {path_length(seg)} steps")

elif page == "Library Insights":
    st.title("📊 Collection & Circulation Insights")
    df=pd.DataFrame(BOOKS)
    total_copies=sum(inventory(b)['total'] for b in BOOKS)
    avail=sum(inventory(b)['available'] for b in BOOKS)
    borrowed=total_copies-avail
    c1,c2,c3,c4=st.columns(4)
    c1.metric("Catalog titles",len(BOOKS)); c2.metric("Physical copies",total_copies); c3.metric("Available copies",avail); c4.metric("Currently unavailable",borrowed)
    st.subheader("Titles by subject")
    st.bar_chart(df['category'].value_counts().sort_values(ascending=False))
    st.subheader("Availability by subject")
    rows=[]
    for cat in get_categories():
        group=[x for x in BOOKS if x['category']==cat]
        rows.append({"Subject":cat,"Titles":len(group),"Total copies":sum(inventory(x)['total'] for x in group),"Available copies":sum(inventory(x)['available'] for x in group)})
    st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
    st.subheader("Catalog sample")
    st.dataframe(pd.DataFrame([{"Title":b['title'],"Author":b['author'],"Subject":b['category'],"Shelf":b['shelf'],"ISBN":b['isbn'],"Year":b['publication_year'],"Available":inventory(b)['available'],"Total copies":inventory(b)['total']} for b in BOOKS]),use_container_width=True,hide_index=True)
