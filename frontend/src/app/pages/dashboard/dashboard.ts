import { Component, signal } from '@angular/core';
import { Auth } from '../../services/auth';
import { Router, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { ChatService, ChatSession } from '../../services/chat';

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

  toggleSidebar() {
    this.isSidebarCollapsed = !this.isSidebarCollapsed;
  }

  constructor(
    private authService: Auth,
    private router: Router,
    private chatService: ChatService
  ) {}
  
  ngOnInit() {
    this.loadChats();
  }

  loadChats() {
    this.chatService.getChats().subscribe({
      next: chats => this.chats.set(chats)
    });
  }

  openChat(id: number) {
    this.router.navigate(['/chats', id]);
  }

  toggleChats() {
    this.isChatsExpanded = !this.isChatsExpanded;
  }


  logout() {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}
