from channels.auth import BaseMiddleware, AuthMiddlewareStack
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.utils.functional import LazyObject


User = get_user_model()


class MyLazyObject(LazyObject):
    """
    Throw a more useful error message when scope['my_var'] is accessed before it's resolved
    """

    def _setup(self):
        raise ValueError("Accessing scope obj before it is ready.")


class MyMiddleware(BaseMiddleware):
    """Предоставляет два метода populate_scope/resolve_scope которые необходимо переопределить"""
    @database_sync_to_async
    def _get_user(self):
        return User.objects.all().first()

    def populate_scope(self, scope): # определяем переменные которые должны находиться в scope
        # pass
        # scope['my_var'] = User.objects.all().first().email
        # scope['my_var'] = 'Hello'
        # scope['my_var'] = None
        scope['my_var'] = MyLazyObject() # lazy объект, который можно создать и потом заполнить

    async def resolve_scope(self, scope): # для выполнения дополнительных действий в scope или записать инфу в бд
        # pass
        # scope['my_var'] = 'Hello3' # hf,jnfnm yt ,eltn
        scope['my_var']._wrapped = await self._get_user() # заполняется не сама переменная, а _wrapped


class SimpleMiddleware:
    def __init__(self, inner):     # методы __init_, __call__ чтобы вызвать класс как функцию - SimpleMiddleware(inner)
        self.inner = inner

    def __call__(self, scope, receive, send):
        # user = User.objects.all().first()
        #return self.inner(dict(scope, my_var="hello")) # добавление переменной в scope
        self.inner(dict(scope, my_var="hello"))
        return self.inner(scope, receive, send)


MyMiddlewareStack = lambda inner: AuthMiddlewareStack(
    MyMiddleware(inner)
)


SimpleMiddlewareStack = lambda inner: AuthMiddlewareStack(
    SimpleMiddleware(inner)
)
