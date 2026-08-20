import { Routes } from '@angular/router';
import { Dashboard } from './dashboard';
import { Websites } from '../websites/websites';

export const DASHBOARD_ROUTES: Routes = [
  {
    path: '',
    component: Dashboard,    
    children: [
      { path: '', redirectTo: 'websites', pathMatch: 'full' },
      {
        path: 'websites',
        component: Websites,
      },
    ],
  },
];