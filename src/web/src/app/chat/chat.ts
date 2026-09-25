import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService, ReportResponse } from '../api.service';

interface ChatMessage {
  role: 'user' | 'assistant';
  text: string;
  response?: ReportResponse;
}

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './chat.html',
  styleUrl: './chat.css',
})
export class Chat {
  input = '';
  loading = false;
  messages: ChatMessage[] = [];

  constructor(private api: ApiService) {}

  send(): void {
    const text = this.input.trim();
    if (!text || this.loading) {
      return;
    }

    this.messages.push({ role: 'user', text });
    this.input = '';
    this.loading = true;

    this.api.askReport(text).subscribe({
      next: (response) => {
        this.messages.push({ role: 'assistant', text: response.report, response });
        this.loading = false;
      },
      error: (err) => {
        this.messages.push({
          role: 'assistant',
          text: 'Something went wrong: ' + (err?.message ?? 'unknown error'),
        });
        this.loading = false;
      },
    });
  }

    extractImageUrl(reportText: string): string {
    const match = reportText.match(/\((\/charts\/[^)]+\.png)\)/);
    return match ? match[1] : '';
  }
}