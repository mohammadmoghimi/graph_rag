import { Routes } from '@angular/router';
import { Login } from './pages/login/login';
import { Dashboard } from './pages/dashboard/dashboard';
import { authGuard } from './guards/auth-guard';
import { Websites } from './pages/websites/websites';


export const routes: Routes = [
  {
    path: 'login',
    component: Login
  },
  {
    path: 'dashboard',
    loadChildren: () =>
      import('./pages/dashboard/dashboard.routes').then((m) => m.DASHBOARD_ROUTES),
    canActivate: [authGuard],
  },
  {
    path: '**',
    redirectTo: '',
  },
];