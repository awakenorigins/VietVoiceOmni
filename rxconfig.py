import reflex as rx

config = rx.Config(
    app_name="VietVoiceOmni",
    # Port 3000/8000 dang busy -> dung port rieng
    frontend_port=3101,
    backend_port=8012,
    # cho phep upload file lon (ebook, audio ref)
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ],
)
