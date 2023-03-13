class Path:
    def __init__(self,**kwargs):
        self.__dict__.update(kwargs)

class Paths:
    def __init__(self):
        self.path_list=[]

    def add_path(self,view,**kwargs):
        new_path=Path(view=view,**kwargs)

        if view.__name__ in [path.view.__name__ for path in self.path_list]:
            raise AssertionError(f"{view.__name__} already has a endpoint function.")
        try:
            for path in self.path_list:
                if kwargs["route_base"] == path.route_base:
                    raise AssertionError(f"{view.__name__} and {path.view.__name__} have the same route base.")
        except AssertionError:
            raise

        self.path_list.append(new_path)
    
    def register(self,app):
        for path in self.path_list:
            methods=path.__dict__.copy()
            del methods["view"]
            path.view.register(app, **methods)