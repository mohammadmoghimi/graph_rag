import { Component, OnInit, signal } from '@angular/core';
import { UserService, AdminUser } from '../../services/user';

@Component({
  selector: 'app-users',
  imports: [],
  templateUrl: './users.html',
  styleUrl: './users.scss'
})
export class Users implements OnInit {
  users = signal<AdminUser[]>([]);
  isLoading = signal(true);
  errorMessage = signal('');

  constructor(private userService: UserService) {}

  ngOnInit() {
    this.loadUsers();
  }

  loadUsers() {
    this.userService.getUsers().subscribe({
      next: users => {
        this.users.set(users);
        this.isLoading.set(false);
      },
      error: () => {
        this.errorMessage.set('خطا در دریافت کاربران.');
        this.isLoading.set(false);
      }
    });
  }

  promoteUser(user: AdminUser) {
    this.userService.promoteUser(user.id).subscribe({
      next: updatedUser => {
        this.users.update(users =>
          users.map(u => u.id === updatedUser.id ? updatedUser : u)
        );
      },
      error: () => {
        this.errorMessage.set('خطا در ارتقای کاربر.');
      }
    });
  }
}