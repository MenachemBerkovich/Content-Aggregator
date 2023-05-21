import pynecone as pc

class FrontConfig(pc.Config):
    pass

config = FrontConfig(
    app_name="front",
    db_url="sqlite:///pynecone.db",
    env=pc.Env.DEV,
)
