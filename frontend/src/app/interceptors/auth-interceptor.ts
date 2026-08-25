import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, switchMap, throwError } from 'rxjs';
import { Auth } from '../services/auth';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const auth = inject(Auth);
  const token = localStorage.getItem('access_token');

  if (!token) {
    return next(req);
  }

  const authReq = req.clone({
    setHeaders: {
      Authorization: `Bearer ${token}`
    }
  });

  return next(authReq).pipe(
    catchError(error => {
      if (error.status !== 401) {
        return throwError(() => error);
      }

      const refreshToken = localStorage.getItem('refresh_token');

      if (!refreshToken) {
        auth.logout();
        return throwError(() => error);
      }

      return auth.refreshToken(refreshToken).pipe(
        switchMap(response => {
          localStorage.setItem('access_token', response.access);

          const retryReq = req.clone({
            setHeaders: {
              Authorization: `Bearer ${response.access}`
            }
          });

          return next(retryReq);
        }),
        catchError(refreshError => {
          auth.logout();
          return throwError(() => refreshError);
        })
      );
    })
  );
};