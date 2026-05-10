import pytest


# ── test_plugin_imports ──

PLUGIN_MODULES = [
    "plugins.group_manager",
    "plugins.group_admin",
    "plugins.group_bind",
    "plugins.user_bind",
    "plugins.config_manager",
]


@pytest.mark.parametrize("module_name", PLUGIN_MODULES)
def test_plugin_imports(nonebot_init, module_name):
    mod = __import__(module_name, fromlist=["__all__"])
    assert mod is not None


# ── test_matchers_registered ──

def test_matchers_registered(nonebot_init):
    matchers = {
        "plugins.group_manager": ["group_instances", "user_location", "vrc_login", "vrc_2fa", "vrc_check"],
        "plugins.group_admin": [
            "gmembers_cmd", "ginvite_cmd", "gkick_cmd", "gban_cmd", "gunban_cmd",
            "grole_cmd", "grequests_cmd", "gaccept_cmd", "greject_cmd",
            "gannounce_cmd", "gdelannounce_cmd", "gaudit_cmd",
        ],
        "plugins.group_bind": ["bindgroup_cmd"],
        "plugins.user_bind": ["bind_cmd", "confirm_cmd", "unbind_cmd", "bindinfo_cmd", "whois_cmd"],
        "plugins.config_manager": ["config_cmd"],
    }

    for module_name, matcher_names in matchers.items():
        mod = __import__(module_name, fromlist=matcher_names)
        for name in matcher_names:
            obj = getattr(mod, name, None)
            assert obj is not None, f"{module_name}.{name} 未注册"


# ── test_config_manager_help ──

def test_config_manager_help(nonebot_init):
    from plugins.config_manager import config_cmd, handle_config
    import inspect
    assert config_cmd is not None
    assert inspect.iscoroutinefunction(handle_config)
