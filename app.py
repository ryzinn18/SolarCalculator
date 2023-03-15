from os.path import abspath
from flask import Flask
from flask_login import LoginManager


def create_app():
    template_dir = abspath("./src/frontend/templates")
    static_dir = abspath("./src/frontend/static")

    app = Flask(
        __name__,
        template_folder=template_dir,
        static_url_path=None,
    )
    app.config["SECRET_KEY"] = "key"
    app.static_url_path = static_dir
    app.static_folder = static_dir

    from src.frontend.views import views
    # from .auth import auth

    app.register_blueprint(views, url_prefix="/")
    # app.register_blueprint(auth, url_prefix="/")

    # from .models import User, Post, Comment, Like

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        # return User.query.get(int(id))
        return None

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
else:
    app = create_app()
