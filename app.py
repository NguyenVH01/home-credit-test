import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import plotly.express as px
from models import User, Review, ReviewCycle, ReviewAssignment, init_db
from auth import authenticate_user, create_user, get_current_user
import os

# Configuration and styling
st.set_page_config(
    page_title="Home Credit 360° Review",
    page_icon="🏢",
    layout="wide",
    menu_items={
        'Get Help': 'https://homecredit.vn/support',
        'Report a bug': 'https://homecredit.vn/bug-report',
        'About': '''
        # Home Credit 360° Review
        Hệ thống đánh giá nhân viên 360° của Home Credit - Đánh giá toàn diện, minh bạch và công bằng.
        
        Version: 1.0.0
        © 2024 Home Credit Vietnam
        '''
    },
    initial_sidebar_state="expanded"
)

# Add logo and header
col1, col2 = st.columns([1, 4])
with col1:
    st.image("https://explore.homecredit.ph/img/HC-Home-Logo.svg", width=150)
with col2:
    st.write("")  # Để tạo khoảng trống cân đối

# Custom CSS for elegant styling
st.markdown("""
    <style>
    /* Light Theme */
    .stApp {
        background-color: #ffffff !important;
    }
    .main {
        padding: 2rem;
        background-color: #ffffff;
    }
    .stButton>button {
        background-color: #0066cc;
        color: white;
        border-radius: 5px;
    }
    .stTextInput>div>div>input {
        border-radius: 5px;
        background-color: #ffffff;
    }
    h1, h2, h3 {
        color: #2c3e50 !important;
    }
    /* Logo styling */
    .stImage {
        margin-top: -60px;
        margin-bottom: -40px;
        padding: 1rem;
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    /* Responsive Design */
    @media screen and (max-width: 768px) {
        .main {
            padding: 1rem;
        }
        .stButton>button {
            width: 100%;
        }
        .stImage {
            margin-top: -30px;
            margin-bottom: -20px;
        }
    }
    /* Print Styles */
    @media print {
        .stButton, .stSidebar {
            display: none !important;
        }
        .main {
            padding: 0;
        }
    }
    /* Custom Branding */
    .stApp > header {
        background-color: #0066cc !important;
    }
    .stApp > header .decoration {
        background-image: none;
    }
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #f8f9fa !important;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa !important;
    }
    /* Form elements */
    .stSelectbox>div>div {
        background-color: #ffffff !important;
    }
    .stTextArea textarea {
        background-color: #ffffff !important;
    }
    .stDateInput>div>div>input {
        background-color: #ffffff !important;
    }
    /* Metric styling */
    .css-1xarl3l {
        background-color: #ffffff !important;
    }
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #f8f9fa !important;
    }
    .streamlit-expanderContent {
        background-color: #ffffff !important;
    }
    /* Hide footer */
    footer {
        visibility: hidden;
    }
    /* Show main menu */
    #MainMenu {
        visibility: visible;
    }
    /* Hide deploy button */
    .stDeployButton {
        display: none !important;
    }
    /* Table styling */
    .dataframe {
        background-color: #ffffff !important;
    }
    .dataframe th {
        background-color: #f8f9fa !important;
    }
    /* Chart background */
    .js-plotly-plot {
        background-color: #ffffff !important;
    }
    </style>
""", unsafe_allow_html=True)

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

# Session state initialization
if 'user' not in st.session_state:
    st.session_state.user = None

def login_page():
    st.title("🏢 Home Credit 360° Review")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### Đăng nhập")
        username = st.text_input("Tên đăng nhập")
        password = st.text_input("Mật khẩu", type="password")
        
        if st.button("Đăng nhập"):
            db = get_db()
            user = authenticate_user(db, username, password)
            if user:
                st.session_state.user = user
                st.experimental_rerun()
            else:
                st.error("Sai tên đăng nhập hoặc mật khẩu")

def admin_dashboard():
    st.title("Quản lý đánh giá 360°")
    
    menu = ["Tổng quan", "Quản lý kỳ đánh giá", "Quản lý người dùng", "Báo cáo"]
    choice = st.sidebar.selectbox("Menu", menu)
    
    if choice == "Tổng quan":
        st.header("Tổng quan hệ thống")
        col1, col2, col3 = st.columns(3)
        
        db = get_db()
        with col1:
            user_count = db.query(User).count()
            st.metric("Tổng số nhân viên", user_count)
        
        with col2:
            active_cycles = db.query(ReviewCycle).filter(ReviewCycle.status == "active").count()
            st.metric("Kỳ đánh giá đang diễn ra", active_cycles)
        
        with col3:
            pending_reviews = db.query(Review).filter(Review.status == "pending").count()
            st.metric("Đánh giá chờ xử lý", pending_reviews)

    elif choice == "Quản lý kỳ đánh giá":
        st.header("Quản lý kỳ đánh giá")
        
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

                # Phân công đánh giá
                if cycle.status == "draft":
                    st.subheader("Phân công đánh giá")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        reviewer = st.selectbox("Người đánh giá", 
                            options=db.query(User).all(),
                            format_func=lambda x: x.full_name,
                            key=f"reviewer_{cycle.id}"
                        )
                    with col2:
                        reviewee = st.selectbox("Người được đánh giá",
                            options=db.query(User).all(),
                            format_func=lambda x: x.full_name,
                            key=f"reviewee_{cycle.id}"
                        )
                    with col3:
                        relationship = st.selectbox("Mối quan hệ",
                            options=["peer", "superior", "subordinate"],
                            key=f"relation_{cycle.id}"
                        )
                    
                    if st.button("Thêm phân công", key=f"assign_{cycle.id}"):
                        if reviewer and reviewee:
                            assignment = ReviewAssignment(
                                review_cycle_id=cycle.id,
                                reviewer_id=reviewer.id,
                                reviewee_id=reviewee.id,
                                relationship_type=relationship,
                                status="pending",
                                due_date=cycle.end_date
                            )
                            db.add(assignment)
                            db.commit()
                            st.success("Đã thêm phân công đánh giá")
                        else:
                            st.error("Vui lòng chọn người đánh giá và người được đánh giá")

    elif choice == "Quản lý người dùng":
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
                        new_user = create_user(db, username, email, password, full_name, department, role)
                        if new_user:
                            st.success("Đã tạo người dùng mới")
                        else:
                            st.error("Tên đăng nhập hoặc email đã tồn tại")
                    else:
                        st.error("Vui lòng điền đầy đủ thông tin")

        # Danh sách người dùng
        db = get_db()
        users = db.query(User).order_by(User.department, User.full_name).all()
        
        # Tạo DataFrame để hiển thị và lọc dữ liệu
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

    elif choice == "Báo cáo":
        st.header("Báo cáo và thống kê")
        
        db = get_db()
        review_cycles = db.query(ReviewCycle).filter(ReviewCycle.status == "completed").all()
        selected_cycle = st.selectbox(
            "Chọn kỳ đánh giá",
            options=review_cycles,
            format_func=lambda x: x.name
        )
        
        if selected_cycle:
            reviews = db.query(Review).filter(
                Review.review_cycle_id == selected_cycle.id,
                Review.status == "approved"
            ).all()
            
            if reviews:
                # Tính điểm trung bình theo từng tiêu chí
                performance_avg = sum(r.performance_score or 0 for r in reviews) / len(reviews)
                leadership_avg = sum(r.leadership_score or 0 for r in reviews) / len(reviews)
                teamwork_avg = sum(r.teamwork_score or 0 for r in reviews) / len(reviews)
                innovation_avg = sum(r.innovation_score or 0 for r in reviews) / len(reviews)
                
                # Vẽ biểu đồ radar
                categories = ['Hiệu suất', 'Lãnh đạo', 'Làm việc nhóm', 'Sáng tạo']
                values = [performance_avg, leadership_avg, teamwork_avg, innovation_avg]
                
                fig = px.line_polar(
                    r=values,
                    theta=categories,
                    line_close=True,
                    range_r=[0,5],
                    title=f"Điểm trung bình - {selected_cycle.name}"
                )
                st.plotly_chart(fig)
                
                # Hiển thị bảng điểm chi tiết
                reviews_data = []
                for review in reviews:
                    reviews_data.append({
                        "Người được đánh giá": review.reviewee.full_name,
                        "Phòng ban": review.reviewee.department,
                        "Điểm hiệu suất": review.performance_score,
                        "Điểm lãnh đạo": review.leadership_score,
                        "Điểm làm việc nhóm": review.teamwork_score,
                        "Điểm sáng tạo": review.innovation_score
                    })
                
                df = pd.DataFrame(reviews_data)
                st.dataframe(df)
            else:
                st.info("Chưa có đánh giá nào được phê duyệt trong kỳ này")

def manager_dashboard():
    st.title("Quản lý đánh giá")
    
    menu = ["Đánh giá chờ duyệt", "Báo cáo nhóm", "Đánh giá đồng nghiệp"]
    choice = st.sidebar.selectbox("Menu", menu)
    
    if choice == "Đánh giá chờ duyệt":
        st.header("Đánh giá chờ phê duyệt")
        db = get_db()
        pending_reviews = db.query(Review).join(User, Review.reviewee_id == User.id).filter(
            Review.status == "pending",
            User.department == st.session_state.user.department
        ).all()
        
        if not pending_reviews:
            st.info("Không có đánh giá nào chờ phê duyệt")
            return
        
        for review in pending_reviews:
            with st.expander(f"Đánh giá cho {review.reviewee.full_name} từ {review.reviewer.full_name}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Điểm hiệu suất", f"{review.performance_score:.1f}/5.0")
                    st.metric("Điểm lãnh đạo", f"{review.leadership_score:.1f}/5.0")
                with col2:
                    st.metric("Điểm làm việc nhóm", f"{review.teamwork_score:.1f}/5.0")
                    st.metric("Điểm sáng tạo", f"{review.innovation_score:.1f}/5.0")
                
                st.subheader("Phản hồi chi tiết")
                st.write("**Điểm mạnh:**")
                st.write(review.strengths)
                st.write("**Cần cải thiện:**")
                st.write(review.areas_for_improvement)
                if review.training_recommendations:
                    st.write("**Đề xuất đào tạo:**")
                    st.write(review.training_recommendations)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Phê duyệt", key=f"approve_{review.id}"):
                        review.status = "approved"
                        review.approved_at = datetime.now()
                        db.commit()
                        st.success("Đã phê duyệt đánh giá")
                        st.experimental_rerun()
                with col2:
                    if st.button("Yêu cầu chỉnh sửa", key=f"reject_{review.id}"):
                        review.status = "rejected"
                        db.commit()
                        st.success("Đã yêu cầu chỉnh sửa đánh giá")
                        st.experimental_rerun()

    elif choice == "Báo cáo nhóm":
        st.header("Báo cáo nhóm")
        db = get_db()
        
        # Lấy danh sách kỳ đánh giá đã hoàn thành
        review_cycles = db.query(ReviewCycle).filter(ReviewCycle.status == "completed").all()
        
        if not review_cycles:
            st.info("Chưa có kỳ đánh giá nào hoàn thành")
            return
        
        selected_cycle = st.selectbox(
            "Chọn kỳ đánh giá",
            options=review_cycles,
            format_func=lambda x: x.name
        )
        
        if selected_cycle:
            # Lấy tất cả đánh giá đã phê duyệt trong phòng ban
            reviews = db.query(Review).join(
                User, Review.reviewee_id == User.id
            ).filter(
                Review.review_cycle_id == selected_cycle.id,
                Review.status == "approved",
                User.department == st.session_state.user.department
            ).all()
            
            if not reviews:
                st.info("Chưa có đánh giá nào được phê duyệt trong kỳ này")
                return
            
            # Tính điểm trung bình theo từng tiêu chí cho phòng ban
            performance_avg = sum(r.performance_score for r in reviews) / len(reviews)
            leadership_avg = sum(r.leadership_score for r in reviews) / len(reviews)
            teamwork_avg = sum(r.teamwork_score for r in reviews) / len(reviews)
            innovation_avg = sum(r.innovation_score for r in reviews) / len(reviews)
            
            # Hiển thị biểu đồ radar cho điểm trung bình phòng ban
            st.subheader(f"Điểm trung bình phòng {st.session_state.user.department}")
            
            categories = ['Hiệu suất', 'Lãnh đạo', 'Làm việc nhóm', 'Sáng tạo']
            values = [performance_avg, leadership_avg, teamwork_avg, innovation_avg]
            
            fig = px.line_polar(
                r=values,
                theta=categories,
                line_close=True,
                range_r=[0,5],
                title=f"Điểm trung bình phòng ban - {selected_cycle.name}"
            )
            st.plotly_chart(fig)
            
            # Hiển thị bảng điểm chi tiết từng nhân viên
            st.subheader("Điểm chi tiết từng nhân viên")
            
            reviews_data = []
            for review in reviews:
                reviews_data.append({
                    "Nhân viên": review.reviewee.full_name,
                    "Người đánh giá": review.reviewer.full_name,
                    "Mối quan hệ": review.relationship_type,
                    "Hiệu suất": review.performance_score,
                    "Lãnh đạo": review.leadership_score,
                    "Làm việc nhóm": review.teamwork_score,
                    "Sáng tạo": review.innovation_score
                })
            
            df = pd.DataFrame(reviews_data)
            st.dataframe(df)
            
            # Xuất báo cáo
            if st.button("Xuất báo cáo Excel"):
                df.to_excel(f"bao_cao_{selected_cycle.name}_{st.session_state.user.department}.xlsx")
                st.success("Đã xuất báo cáo thành công")

    elif choice == "Đánh giá đồng nghiệp":
        # Sử dụng lại chức năng đánh giá đồng nghiệp của nhân viên
        employee_dashboard()

def employee_dashboard():
    st.title("Đánh giá 360°")
    
    menu = ["Đánh giá của tôi", "Đánh giá đồng nghiệp"]
    choice = st.sidebar.selectbox("Menu", menu)
    
    if choice == "Đánh giá của tôi":
        st.header("Đánh giá của tôi")
        db = get_db()
        my_reviews = db.query(Review).filter(Review.reviewee_id == st.session_state.user.id).all()
        
        for review in my_reviews:
            with st.expander(f"Đánh giá từ {review.reviewer.full_name}"):
                st.write(f"Trạng thái: {review.status}")
                if review.status == "approved":
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Điểm hiệu suất", f"{review.performance_score:.1f}/5.0")
                        st.metric("Điểm lãnh đạo", f"{review.leadership_score:.1f}/5.0")
                    with col2:
                        st.metric("Điểm làm việc nhóm", f"{review.teamwork_score:.1f}/5.0")
                        st.metric("Điểm sáng tạo", f"{review.innovation_score:.1f}/5.0")
                    
                    st.subheader("Phản hồi chi tiết")
                    st.write("**Điểm mạnh:**")
                    st.write(review.strengths)
                    st.write("**Cần cải thiện:**")
                    st.write(review.areas_for_improvement)
                    if review.training_recommendations:
                        st.write("**Đề xuất đào tạo:**")
                        st.write(review.training_recommendations)

    elif choice == "Đánh giá đồng nghiệp":
        st.header("Đánh giá đồng nghiệp")
        db = get_db()
        
        # Lấy danh sách các phân công đánh giá đang chờ xử lý
        pending_assignments = db.query(ReviewAssignment).join(ReviewCycle).filter(
            ReviewAssignment.reviewer_id == st.session_state.user.id,
            ReviewAssignment.status == "pending",
            ReviewCycle.status == "active"
        ).all()
        
        if not pending_assignments:
            st.info("Bạn không có đánh giá nào cần thực hiện")
            return
        
        for assignment in pending_assignments:
            with st.expander(f"Đánh giá cho {assignment.reviewee.full_name} - {assignment.review_cycle.name}"):
                # Kiểm tra xem đã có review chưa
                existing_review = db.query(Review).filter(
                    Review.review_cycle_id == assignment.review_cycle_id,
                    Review.reviewer_id == assignment.reviewer_id,
                    Review.reviewee_id == assignment.reviewee_id
                ).first()
                
                if existing_review:
                    st.warning("Bạn đã thực hiện đánh giá này")
                    continue
                
                with st.form(f"review_form_{assignment.id}"):
                    st.subheader("Đánh giá định lượng")
                    col1, col2 = st.columns(2)
                    with col1:
                        performance_score = st.slider(
                            "Điểm hiệu suất công việc",
                            min_value=1.0,
                            max_value=5.0,
                            step=0.1,
                            help="Đánh giá khả năng hoàn thành công việc, chất lượng và hiệu quả"
                        )
                        leadership_score = st.slider(
                            "Điểm kỹ năng lãnh đạo",
                            min_value=1.0,
                            max_value=5.0,
                            step=0.1,
                            help="Đánh giá khả năng lãnh đạo, định hướng và tạo động lực"
                        )
                    with col2:
                        teamwork_score = st.slider(
                            "Điểm làm việc nhóm",
                            min_value=1.0,
                            max_value=5.0,
                            step=0.1,
                            help="Đánh giá khả năng hợp tác, giao tiếp và đóng góp cho nhóm"
                        )
                        innovation_score = st.slider(
                            "Điểm sáng tạo & đổi mới",
                            min_value=1.0,
                            max_value=5.0,
                            step=0.1,
                            help="Đánh giá khả năng đổi mới, sáng tạo và cải tiến trong công việc"
                        )
                    
                    st.subheader("Đánh giá định tính")
                    strengths = st.text_area(
                        "Điểm mạnh",
                        help="Liệt kê những điểm mạnh và thành tích nổi bật"
                    )
                    areas_for_improvement = st.text_area(
                        "Điểm cần cải thiện",
                        help="Đề xuất những lĩnh vực cần phát triển thêm"
                    )
                    training_recommendations = st.text_area(
                        "Đề xuất đào tạo",
                        help="Đề xuất các khóa học hoặc hình thức đào tạo phù hợp"
                    )
                    
                    if st.form_submit_button("Gửi đánh giá"):
                        if not (strengths and areas_for_improvement):
                            st.error("Vui lòng điền đầy đủ phần đánh giá định tính")
                            return
                        
                        review = Review(
                            review_cycle_id=assignment.review_cycle_id,
                            reviewer_id=assignment.reviewer_id,
                            reviewee_id=assignment.reviewee_id,
                            relationship_type=assignment.relationship_type,
                            performance_score=performance_score,
                            leadership_score=leadership_score,
                            teamwork_score=teamwork_score,
                            innovation_score=innovation_score,
                            strengths=strengths,
                            areas_for_improvement=areas_for_improvement,
                            training_recommendations=training_recommendations,
                            status="pending",
                            submitted_at=datetime.now()
                        )
                        
                        assignment.status = "completed"
                        db.add(review)
                        db.commit()
                        st.success("Đã gửi đánh giá thành công")
                        st.experimental_rerun()

def main():
    if st.session_state.user is None:
        login_page()
    else:
        st.sidebar.write(f"Xin chào, {st.session_state.user.full_name}")
        if st.sidebar.button("Đăng xuất"):
            st.session_state.user = None
            st.experimental_rerun()
        
        if st.session_state.user.role == "admin":
            admin_dashboard()
        elif st.session_state.user.role == "manager":
            manager_dashboard()
        else:
            employee_dashboard()

if __name__ == "__main__":
    main() 