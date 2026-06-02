import streamlit as st


def aplicar_estilos():
    st.markdown(
        """
        <style>
        /* ── Sidebar fondo celeste ── */
        [data-testid="stSidebar"] {
            background-color: #DBEAFE;
        }

        /* ── Encabezados dentro del sidebar ── */
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] p {
            color: #1E3A5F;
        }

        /* ── Items de navegación: texto capitalizado ── */
        [data-testid="stSidebarNavLink"] span,
        [data-testid="stSidebarNavLink"] p {
            text-transform: capitalize;
            font-weight: 500;
            font-size: 0.95rem;
            color: #1E3A5F;
        }

        /* ── Hover en items de navegación ── */
        [data-testid="stSidebarNavLink"]:hover {
            background-color: #1565C0 !important;
            border-radius: 8px;
        }
        [data-testid="stSidebarNavLink"]:hover span,
        [data-testid="stSidebarNavLink"]:hover p {
            color: #FFFFFF !important;
        }

        /* ── Item activo (página actual) ── */
        [data-testid="stSidebarNavLink"][aria-current="page"] {
            background-color: #1976D2 !important;
            border-radius: 8px;
        }
        [data-testid="stSidebarNavLink"][aria-current="page"] span,
        [data-testid="stSidebarNavLink"][aria-current="page"] p {
            color: #FFFFFF !important;
            font-weight: 700;
        }

        /* ── Divider del sidebar ── */
        [data-testid="stSidebar"] hr {
            border-color: #93C5FD;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
