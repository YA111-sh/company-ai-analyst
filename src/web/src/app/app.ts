import { Component, signal } from '@angular/core';
import { Chat } from './chat/chat';


@Component({
  selector: 'app-root',
  imports: [Chat],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  protected readonly title = signal('web');
}




