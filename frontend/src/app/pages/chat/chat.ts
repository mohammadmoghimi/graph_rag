import { Component, OnInit } from '@angular/core';
import { ChatService, ChatSession } from '../../services/chat';
import { ActivatedRoute } from '@angular/router';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-chat',
  imports: [FormsModule],
  templateUrl: './chat.html',
  styleUrl: './chat.scss',
})
export class Chat implements OnInit{
  chat?: ChatSession;
  message = '';
  isLoading = true;

  constructor(
    private route: ActivatedRoute,
    private chatService: ChatService
  ) {}

  ngOnInit() {
    const id = Number(this.route.snapshot.paramMap.get('id'));

    this.chatService.getChat(id).subscribe({
      next: chat => {
        this.chat = chat;
        this.isLoading = false;
      },
      error: () => {
        this.isLoading = false;
      }
    });
  }

  sendMessage() {
    if (!this.message.trim() || !this.chat) return;

    console.log(this.message);
    this.message = '';
  }
}
