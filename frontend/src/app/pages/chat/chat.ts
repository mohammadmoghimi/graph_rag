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

  messages: { role: string; content: string }[] = [];
  isSending = false;

  sendMessage() {
    const question = this.message.trim();

    if (!question || !this.chat || this.isSending) return;

    this.messages.push({
      role: 'user',
      content: question
    });

    this.message = '';
    this.isSending = true;

    this.chatService.ask(this.chat.id, question).subscribe({
      next: response => {
        this.messages.push({
          role: 'assistant',
          content: response.answer
        });

        this.isSending = false;
      },
      error: error => {
        this.messages.push({
          role: 'assistant',
          content: error.error?.error || 'خطا در دریافت پاسخ.'
        });

        this.isSending = false;
      }
    });
  }
}
