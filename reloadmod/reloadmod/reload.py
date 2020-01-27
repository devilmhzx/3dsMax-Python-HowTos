import sys
import importlib
import inspect
import pymxs

FORCE_SKIP = []

def non_builtin():
    """Return a set of all modules names that are not builtins and not
    importlib related."""
    skip = set(
        # filter out the builtins that should not be reloaded anyway
        list(sys.builtin_module_names) + 
        # filter out importlib that if reloaded breaks the whole thing
        list(filter(lambda k: k.find("importlib") >= 0, sys.modules.keys())) +
        FORCE_SKIP)
    return set(filter(lambda k: not (k in skip) and not is_builtin(k), sys.modules.keys()))

def reload_many(keys):
    """Reload multiple packages by name"""
    for k in keys:
        try:
            importlib.invalidate_caches()
            importlib.reload(sys.modules[k])
            print("module {} reloaded".format(k));
        except NotImplementedError:
            print("     *module {} could not be reloaded because Not Implemented".format(k))
        except Exception as e:
            print("     *module {} could not be reloaded because {}".format(k, str(e)))

def is_builtin(key):
    """Test builtin using inspect (some modules not seen
    as builtin in sys.builtin_module_names may look builtin
    anyway to inspect and in this case we want to filter them
    out."""
    try:
        inspect.getfile(sys.modules[key])
    except TypeError:
        return True
    return False

def module_path(key):
    """Return the loading path of a module"""
    return inspect.getfile(sys.modules[key])

def prefixed_by(apath, some_paths):
    """Check if a path is a a subpath of one of the provided paths"""
    return len([ p for p in some_paths if (apath.find(p) == 0)]) > 0

def filter_out_paths(keys, fullpaths):
    """Filter out paths prefixed by some path"""
    return set([k for k in keys if not prefixed_by(module_path(k), fullpaths)])

def filter_out_string(keys, string):
    """Filter out paths that contain a specific string"""
    return set([k for k in keys if module_path(k).find(string) < 0])

def show_location(title, keys):
    """Show the location of a set of packages"""
    print(title)
    for k in keys:
        print("{} loaded from {}".format(k, module_path(k)))

NON_BUILTIN = non_builtin()
NON_MAX = filter_out_paths(NON_BUILTIN, [pymxs.runtime.getdir(pymxs.runtime.name("maxroot"))])
DEV_ONLY = filter_out_string(NON_MAX, "site-packages") 
