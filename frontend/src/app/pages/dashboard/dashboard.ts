import { Component, signal } from '@angular/core';
import { Auth } from '../../services/auth';
import { ActivatedRoute, NavigationEnd, Router, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { ChatService, ChatSession } from '../../services/chat';
import { filter } from 'rxjs';
// import { AdminUser } from '../../services/user';
import {User} from '../../services/auth'
@Component({
  selector: 'app-dashboard',
  imports: [RouterLink, RouterLinkActive, RouterOutlet],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.scss',
})
export class Dashboard {
  isSidebarCollapsed = false;
  isChatsExpanded = false;
  chats = signal<ChatSession[]>([]);
  activeChatId = signal<number | null>(null);
  currentUser = signal<User | null>(null);
  
  toggleSidebar() {
    this.isSidebarCollapsed = !this.isSidebarCollapsed;
  }

  constructor(
    private authService: Auth,
    private router: Router,
    private chatService: ChatService,
    private route: ActivatedRoute
  ) {}
  
  ngOnInit() {
    this.getCurrentUser();
    this.loadChats();

    this.setActiveChatFromRoute();

    this.router.events
      .pipe(filter(event => event instanceof NavigationEnd))
      .subscribe(() => {
        this.setActiveChatFromRoute();
      });
  }

  getCurrentUser() {
    this.authService.getCurrentUser().subscribe({
      next: user => this.currentUser.set(user) ,
      complete: () => console.log('Current user loaded' , this.currentUser())
    });
  }

  loadChats() {
    this.chatService.getChats().subscribe({
      next: chats => this.chats.set(chats)
    });
  }

  openChat(id: number) {
    this.activeChatId.set(id);
    this.router.navigate(['/chats', id]);
  }

  private setActiveChatFromRoute() {
    const id = this.route.firstChild?.snapshot.paramMap.get('id');
    if (id) {
      this.activeChatId.set(Number(id));
    } else {
      this.activeChatId.set(null);
    }
  }

  toggleChats() {
    this.isChatsExpanded = !this.isChatsExpanded;
  }


  logout() {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}
