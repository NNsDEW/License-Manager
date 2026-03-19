import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap, catchError, of } from 'rxjs';

const BASE_URL = 'http://localhost:8000/api';
const TOKEN_KEY = 'licensing_token';

export interface UserInfo {
  id: number;
  username: string;
  is_staff: boolean;
  is_superuser: boolean;
}

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private currentUser: UserInfo | null = null;

  constructor(private http: HttpClient) {}

  getToken(): string | null {
    return localStorage.getItem(TOKEN_KEY);
  }

  isLoggedIn(): boolean {
    return !!this.getToken();
  }

  login(username: string, password: string): Observable<{ token: string }> {
    return this.http.post<{ token: string }>(`${BASE_URL}/auth/token/`, { username, password }).pipe(
      tap((res) => {
        localStorage.setItem(TOKEN_KEY, res.token);
        this.currentUser = null;
      })
    );
  }

  register(username: string, password: string, email?: string): Observable<{ token: string; username: string; is_staff: boolean }> {
    return this.http
      .post<{ token: string; username: string; is_staff: boolean }>(`${BASE_URL}/auth/register/`, {
        username,
        password,
        email: email || undefined,
      })
      .pipe(
        tap((res) => {
          localStorage.setItem(TOKEN_KEY, res.token);
          // id подтянется при последующем вызове getCurrentUser()
          this.currentUser = { id: 0, username: res.username, is_staff: res.is_staff, is_superuser: false };
        })
      );
  }

  logout(): void {
    localStorage.removeItem(TOKEN_KEY);
    this.currentUser = null;
  }

  getCurrentUser(): Observable<UserInfo | null> {
    if (this.currentUser) return of(this.currentUser);
    const token = this.getToken();
    if (!token) return of(null);
    return this.http.get<UserInfo>(`${BASE_URL}/auth/me/`).pipe(
      tap((user) => (this.currentUser = user)),
      catchError(() => {
        this.logout();
        return of(null);
      })
    );
  }

  getCachedUser(): UserInfo | null {
    return this.currentUser;
  }

  isStaff(): boolean {
    return !!this.currentUser?.is_staff;
  }
}
