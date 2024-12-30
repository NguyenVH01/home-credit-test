import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import plotly.express as px
import plotly.graph_objects as go
from models import User, Review, ReviewCycle, ReviewAssignment, init_db
from auth import authenticate_user, create_user, get_current_user
import os
import json
from reports import (
    get_department_scores,
    get_top_performers,
    get_review_completion_status,
    get_training_recommendations,
    get_improvement_areas
)

# Configuration and styling
st.set_page_config(
    page_title="Home Credit 360° Review",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "user" not in st.session_state:
    st.session_state.user = None

# Session persistence
def load_session():
    try:
        with open('.session.json', 'r') as f:
            return json.load(f)
    except:
        return {}

def save_session(session_data):
    with open('.session.json', 'w') as f:
        json.dump(session_data, f)

# Load saved session if exists
if 'user' not in st.session_state:
    saved_session = load_session()
    if 'user' in saved_session:
        db = get_db()
        user = db.query(User).filter(User.id == saved_session['user']['id']).first()
        if user:
            st.session_state.user = user

# Header with logo and welcome message
col1, col2, col3 = st.columns([1, 3, 1])
with col1:
    st.image("https://explore.homecredit.ph/img/HC-Home-Logo.svg", width=150)
with col2:
    st.markdown("<h1 style='text-align: center; margin-top: 20px;'>Home Credit 360° Review</h1>", unsafe_allow_html=True)

# Database setup
DATABASE_URL = "sqlite:///360review.db"
engine = init_db(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

def login_page():
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
            <div style='background-color: white; padding: 2rem; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                <h2 style='text-align: center; color: #2c3e50; margin-bottom: 2rem;'>Đăng nhập</h2>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("Tên đăng nhập", placeholder="Nhập tên đăng nhập")
            password = st.text_input("Mật khẩu", type="password", placeholder="Nhập mật khẩu")
            remember = st.checkbox("Ghi nhớ đăng nhập")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.form_submit_button("Đăng nhập", use_container_width=True):
                    if username and password:
                        db = get_db()
                        user = authenticate_user(db, username, password)
                        if user:
                            st.session_state.user = user
                            if remember:
                                save_session({
                                    'user': {
                                        'id': user.id,
                                        'username': user.username,
                                        'role': user.role
                                    }
                                })
                            st.experimental_rerun()
                        else:
                            st.error("Sai tên đăng nhập hoặc mật khẩu")
                    else:
                        st.warning("Vui lòng điền đầy đủ thông tin đăng nhập")

def hr_reports():
    st.header("Báo cáo HR")
    
    # Chọn chu kỳ đánh giá
    db = get_db()
    review_cycles = db.query(ReviewCycle).all()
    
    if not review_cycles:
        st.warning("Chưa có kỳ đánh giá nào được tạo")
        return
        
    cycle_names = [cycle.name for cycle in review_cycles]
    selected_cycle = st.selectbox("Chọn chu kỳ đánh giá", cycle_names)
    selected_cycle_id = next((cycle.id for cycle in review_cycles if cycle.name == selected_cycle), None)
    
    if not selected_cycle_id:
        st.error("Không tìm thấy kỳ đánh giá")
        return
    
    # Hiển thị tiến độ đánh giá
    st.subheader("Tiến độ đánh giá")
    completion_status = get_review_completion_status(db, selected_cycle_id)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Tổng số đánh giá", completion_status['total_reviews'])
    with col2:
        st.metric("Đã hoàn thành", completion_status['completed_reviews'])
    with col3:
        st.metric("Tỷ lệ hoàn thành", f"{completion_status['completion_rate']:.1f}%")
    
    # Biểu đồ điểm trung bình theo phòng ban
    st.subheader("Điểm trung bình theo phòng ban")
    dept_scores = get_department_scores(db, selected_cycle_id)
    if dept_scores:
        df_dept = pd.DataFrame(dept_scores)
        fig = px.bar(
            df_dept,
            x='department',
            y=['avg_performance', 'avg_leadership', 'avg_teamwork', 'avg_innovation'],
            title='Điểm trung bình theo phòng ban',
            labels={
                'department': 'Phòng ban',
                'value': 'Điểm trung bình',
                'variable': 'Tiêu chí'
            },
            barmode='group'
        )
        st.plotly_chart(fig)
    
    # Top performers
    st.subheader("Top nhân viên xuất sắc")
    top_performers = get_top_performers(db, selected_cycle_id, limit=5)
    if top_performers:
        df_top = pd.DataFrame(top_performers)
        fig = go.Figure(data=[
            go.Table(
                header=dict(values=['Họ tên', 'Phòng ban', 'Hiệu suất', 'Lãnh đạo', 'Làm việc nhóm', 'Đổi mới'],
                          fill_color='paleturquoise',
                          align='left'),
                cells=dict(values=[df_top.full_name, df_top.department,
                                 df_top.avg_performance.round(2),
                                 df_top.avg_leadership.round(2),
                                 df_top.avg_teamwork.round(2),
                                 df_top.avg_innovation.round(2)],
                         fill_color='lavender',
                         align='left'))
        ])
        st.plotly_chart(fig)
    
    # Đề xuất đào tạo
    st.subheader("Đề xuất đào tạo phổ biến")
    training_recs = get_training_recommendations(db, selected_cycle_id)
    if training_recs:
        df_training = pd.DataFrame(training_recs)
        fig = px.bar(
            df_training.head(10),
            x='recommendation',
            y='count',
            title='Top 10 đề xuất đào tạo',
            labels={
                'recommendation': 'Đề xuất',
                'count': 'Số lượt đề xuất'
            }
        )
        st.plotly_chart(fig)
    
    # Lĩnh vực cần cải thiện
    st.subheader("Lĩnh vực cần cải thiện")
    improvement_areas = get_improvement_areas(db, selected_cycle_id)
    if improvement_areas:
        df_areas = pd.DataFrame(improvement_areas)
        fig = px.bar(
            df_areas.head(10),
            x='area',
            y='count',
            title='Top 10 lĩnh vực cần cải thiện',
            labels={
                'area': 'Lĩnh vực',
                'count': 'Số lượt đề cập'
            }
        )
        st.plotly_chart(fig)

def admin_dashboard():
    # Dashboard header
    st.markdown("""
        <div style='background-color: white; padding: 1.5rem; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 2rem;'>
            <h1 style='color: #2c3e50; margin: 0;'>Quản trị hệ thống</h1>
        </div>
    """, unsafe_allow_html=True)
    
    # Navigation with icons
    menu = {
        "Quản lý chu kỳ đánh giá": "📅",
        "Quản lý người dùng": "👥",
        "Báo cáo HR": "📊"
    }
    
    choice = st.sidebar.selectbox(
        "Chức năng",
        list(menu.keys()),
        format_func=lambda x: f"{menu[x]} {x}"
    )
    
    # Display current section
    st.markdown(f"### {menu[choice]} {choice}")
    
    if choice == "Quản lý chu kỳ đánh giá":
        manage_review_cycles()
    elif choice == "Quản lý người dùng":
        manage_users()
    elif choice == "Báo cáo HR":
        hr_reports()

def manager_dashboard():
    # Dashboard header
    st.markdown("""
        <div style='background-color: white; padding: 1.5rem; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 2rem;'>
            <h1 style='color: #2c3e50; margin: 0;'>Quản lý đánh giá</h1>
        </div>
    """, unsafe_allow_html=True)
    
    # Navigation with icons
    menu = {
        "Đánh giá chờ duyệt": "⏳",
        "Báo cáo nhóm": "📊",
        "Đánh giá đồng nghiệp": "👥"
    }
    
    choice = st.sidebar.selectbox(
        "Menu",
        list(menu.keys()),
        format_func=lambda x: f"{menu[x]} {x}"
    )
    
    # Display current section
    st.markdown(f"### {menu[choice]} {choice}")

def employee_dashboard():
    # Dashboard header
    st.markdown("""
        <div style='background-color: white; padding: 1.5rem; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 2rem;'>
            <h1 style='color: #2c3e50; margin: 0;'>Đánh giá 360°</h1>
        </div>
    """, unsafe_allow_html=True)
    
    # Navigation with icons
    menu = {
        "Đánh giá của tôi": "📋",
        "Đánh giá đồng nghiệp": "👥"
    }
    
    choice = st.sidebar.selectbox(
        "Menu",
        list(menu.keys()),
        format_func=lambda x: f"{menu[x]} {x}"
    )
    
    # Display current section
    st.markdown(f"### {menu[choice]} {choice}")

def manage_review_cycles():
    st.header("Quản lý chu kỳ đánh giá")
    
    # Form tạo kỳ đánh giá mới
    with st.expander("Tạo kỳ đánh giá mới"):
        with st.form("new_review_cycle"):
            cycle_name = st.text_input("Tên kỳ đánh giá")
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Ngày bắt đầu")
            with col2:
                end_date = st.date_input("Ngày kết thúc")
            
            if st.form_submit_button("Tạo kỳ đánh giá"):
                if cycle_name and start_date and end_date:
                    db = get_db()
                    new_cycle = ReviewCycle(
                        name=cycle_name,
                        start_date=datetime.combine(start_date, datetime.min.time()),
                        end_date=datetime.combine(end_date, datetime.max.time()),
                        status="draft",
                        created_by=st.session_state.user.id
                    )
                    db.add(new_cycle)
                    db.commit()
                    st.success("Đã tạo kỳ đánh giá mới")
                else:
                    st.error("Vui lòng điền đầy đủ thông tin")

    # Danh sách kỳ đánh giá
    db = get_db()
    review_cycles = db.query(ReviewCycle).order_by(ReviewCycle.created_at.desc()).all()
    
    for cycle in review_cycles:
        with st.expander(f"{cycle.name} ({cycle.status})"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write("Ngày bắt đầu:", cycle.start_date.strftime("%d/%m/%Y"))
            with col2:
                st.write("Ngày kết thúc:", cycle.end_date.strftime("%d/%m/%Y"))
            with col3:
                if cycle.status == "draft":
                    if st.button("Kích hoạt", key=f"activate_{cycle.id}"):
                        cycle.status = "active"
                        db.commit()
                        st.success("Đã kích hoạt kỳ đánh giá")
                        st.experimental_rerun()
                elif cycle.status == "active":
                    if st.button("Kết thúc", key=f"complete_{cycle.id}"):
                        cycle.status = "completed"
                        db.commit()
                        st.success("Đã kết thúc kỳ đánh giá")
                        st.experimental_rerun()

def manage_users():
    st.header("Quản lý người dùng")
    
    # Form tạo người dùng mới
    with st.expander("Thêm người dùng mới"):
        with st.form("new_user"):
            col1, col2 = st.columns(2)
            with col1:
                username = st.text_input("Tên đăng nhập")
                email = st.text_input("Email")
                password = st.text_input("Mật khẩu", type="password")
            with col2:
                full_name = st.text_input("Họ và tên")
                department = st.text_input("Phòng ban")
                role = st.selectbox("Vai trò", ["employee", "manager", "admin"])
            
            if st.form_submit_button("Tạo người dùng"):
                if username and email and password and full_name:
                    db = get_db()
                    new_user = create_user(db, username, password, email, full_name, department, role)
                    if new_user:
                        st.success("Đã tạo người dùng mới")
                    else:
                        st.error("Tên đăng nhập hoặc email đã tồn tại")
                else:
                    st.error("Vui lòng điền đầy đủ thông tin")

    # Danh sách người dùng
    db = get_db()
    users = db.query(User).order_by(User.department, User.full_name).all()
    
    users_data = []
    for user in users:
        users_data.append({
            "ID": user.id,
            "Họ và tên": user.full_name,
            "Email": user.email,
            "Phòng ban": user.department,
            "Vai trò": user.role,
            "Ngày tạo": user.created_at.strftime("%d/%m/%Y")
        })
    
    df = pd.DataFrame(users_data)
    st.dataframe(df)

def main():
    if st.session_state.user is None:
        login_page()
    else:
        # User info in sidebar
        st.sidebar.markdown(f"""
            <div style='background-color: white; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;'>
                <h4 style='color: #2c3e50; margin: 0;'>👋 Xin chào,</h4>
                <p style='color: #0066cc; font-weight: 500; margin: 0.5rem 0;'>{st.session_state.user.full_name}</p>
                <p style='color: #6c757d; font-size: 0.9rem; margin: 0;'>{st.session_state.user.department}</p>
            </div>
        """, unsafe_allow_html=True)
        
        if st.sidebar.button("📤 Đăng xuất", use_container_width=True):
            st.session_state.user = None
            # Clear saved session
            if os.path.exists('.session.json'):
                os.remove('.session.json')
            st.experimental_rerun()
        
        st.sidebar.markdown("---")
        
        if st.session_state.user.role == "admin":
            admin_dashboard()
        elif st.session_state.user.role == "manager":
            manager_dashboard()
        else:
            employee_dashboard()

if __name__ == "__main__":
    main() 