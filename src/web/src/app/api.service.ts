import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface ToolCall {
  id: string;
  tool: string;
  arguments: Record<string, unknown>;
}

export interface ReportResponse {
  user_request: string;
  findings: string;
  report: string;
  verified: boolean;
  tool_calls: ToolCall[];
}

@Injectable({ providedIn: 'root' })
export class ApiService {
  constructor(private http: HttpClient) {}

  askReport(message: string): Observable<ReportResponse> {
    return this.http.post<ReportResponse>('/api/report', { message });
  }
}