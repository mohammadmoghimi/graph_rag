import { Routes } from '@angular/router';
import { Dashboard } from './dashboard';
import { Websites } from '../websites/websites';
import { Chat } from '../chat/chat';
import { Users } from '../users/users';
import { DashboardStatistics } from '../dashboard-statistics/dashboard-statistics';
import { Documents } from '../documents/documents';

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
      {
        path:'chats/:id',
        component:Chat
      },
      {
        path:'users',
        component:Users
      },
      {
        path: 'statistics',
        component: DashboardStatistics
      },
      {
        path:'upload-document',
        component:Documents
      }
    ],
  },
];