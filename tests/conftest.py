from hypothesis import settings

settings.register_profile('no-deadline', deadline=None)
settings.load_profile('no-deadline')
