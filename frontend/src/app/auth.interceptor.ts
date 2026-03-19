import { HttpInterceptorFn } from '@angular/common/http';

const TOKEN_KEY = 'licensing_token';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const token = localStorage.getItem(TOKEN_KEY);
  if (token && !req.url.includes('/auth/token/') && !req.url.includes('/auth/register/')) {
    req = req.clone({
      setHeaders: { Authorization: `Token ${token}` },
    });
  }
  return next(req);
};
