import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

const BASE_URL = 'http://localhost:8000/api';

export interface LicenseGenerateRequest {
  client_id: number;
  product_id: number;
  license_type_id: number;
  order_id?: number;
  max_activations?: number;
}

export interface LicenseValidateRequest {
  key: string;
  product_code: string;
  device_id?: string;
  device_name?: string;
}

export interface LicenseValidateByKeyRequest {
  key: string;
  device_id?: string;
  device_name?: string;
}

export interface SupportTicketPayload {
  client?: number | null;
  license?: number | null;
  subject: string;
  description: string;
  priority?: 'LOW' | 'MEDIUM' | 'HIGH';
  status?: 'OPEN' | 'IN_PROGRESS' | 'RESOLVED' | 'CLOSED';
  assigned_to?: number | null;
}

@Injectable({
  providedIn: 'root',
})
export class ApiService {
  constructor(private http: HttpClient) {}

  private ownerParams(ownerId?: number | null): HttpParams | undefined {
    if (ownerId == null) return undefined;
    return new HttpParams().set('owner', String(ownerId));
  }

  /** Список пользователей (только для админа). */
  getUsers(): Observable<{ id: number; username: string; is_staff: boolean }[]> {
    return this.http.get<any[]>(`${BASE_URL}/auth/users/`);
  }

  getClients(ownerId?: number | null): Observable<any[]> {
    const params = this.ownerParams(ownerId);
    return this.http.get<any[]>(`${BASE_URL}/clients/`, params ? { params } : undefined);
  }

  getProducts(ownerId?: number | null): Observable<any[]> {
    const params = this.ownerParams(ownerId);
    return this.http.get<any[]>(`${BASE_URL}/products/`, params ? { params } : undefined);
  }

  getLicenseTypes(ownerId?: number | null): Observable<any[]> {
    const params = this.ownerParams(ownerId);
    return this.http.get<any[]>(`${BASE_URL}/license-types/`, params ? { params } : undefined);
  }

  getPricing(): Observable<any[]> {
    return this.http.get<any[]>(`${BASE_URL}/pricing/`);
  }

  getOrders(ownerId?: number | null): Observable<any[]> {
    const params = this.ownerParams(ownerId);
    return this.http.get<any[]>(`${BASE_URL}/orders/`, params ? { params } : undefined);
  }

  getLicenses(ownerId?: number | null): Observable<any[]> {
    const params = this.ownerParams(ownerId);
    return this.http.get<any[]>(`${BASE_URL}/licenses/`, params ? { params } : undefined);
  }

  getOrderItems(): Observable<any[]> {
    return this.http.get<any[]>(`${BASE_URL}/order-items/`);
  }

  generateLicense(payload: LicenseGenerateRequest): Observable<any> {
    // Backend: generate/validate actions live on SupportTicketViewSet.
    // Calling /licenses/* triggers IsAdminOrReadOnly and returns "You do not have permission...".
    return this.http.post(`${BASE_URL}/support-tickets/generate/`, payload);
  }

  validateLicense(payload: LicenseValidateRequest): Observable<any> {
    return this.http.post(`${BASE_URL}/support-tickets/validate/`, payload);
  }

  validateLicenseByKey(payload: LicenseValidateByKeyRequest): Observable<any> {
    return this.http.post(`${BASE_URL}/support-tickets/validate-key/`, payload);
  }

  renewLicense(licenseId: number): Observable<any> {
    return this.http.post(`${BASE_URL}/licenses/${licenseId}/renew/`, {});
  }

  createClient(data: { name: string; client_type: string; contact_email: string; contact_phone?: string; country?: string }): Observable<any> {
    return this.http.post(`${BASE_URL}/clients/`, data);
  }

  updateClient(id: number, data: { name: string; client_type: string; contact_email: string; contact_phone?: string; country?: string }): Observable<any> {
    return this.http.put(`${BASE_URL}/clients/${id}/`, data);
  }

  deleteClient(id: number): Observable<void> {
    return this.http.delete<void>(`${BASE_URL}/clients/${id}/`);
  }

  createProduct(data: { name: string; code: string; is_active?: boolean }): Observable<any> {
    return this.http.post(`${BASE_URL}/products/`, { ...data, is_active: data.is_active !== false });
  }

  updateProduct(id: number, data: { name: string; code: string; is_active?: boolean }): Observable<any> {
    return this.http.put(`${BASE_URL}/products/${id}/`, { ...data, is_active: data.is_active !== false });
  }

  deleteProduct(id: number): Observable<void> {
    return this.http.delete<void>(`${BASE_URL}/products/${id}/`);
  }

  createLicenseType(data: {
    name: string;
    description?: string;
    max_devices?: number;
    has_expiration?: boolean;
    duration_days?: number;
    renewable?: boolean;
  }): Observable<any> {
    return this.http.post(`${BASE_URL}/license-types/`, data);
  }

  updateLicenseType(id: number, data: {
    name: string;
    description?: string;
    max_devices?: number;
    has_expiration?: boolean;
    duration_days?: number;
    renewable?: boolean;
  }): Observable<any> {
    return this.http.put(`${BASE_URL}/license-types/${id}/`, data);
  }

  deleteLicenseType(id: number): Observable<void> {
    return this.http.delete<void>(`${BASE_URL}/license-types/${id}/`);
  }

  deleteLicense(id: number): Observable<void> {
    return this.http.delete<void>(`${BASE_URL}/licenses/${id}/`);
  }

  /** Тикеты поддержки */
  getSupportTickets(): Observable<any[]> {
    return this.http.get<any[]>(`${BASE_URL}/support-tickets/`);
  }

  createSupportTicket(data: SupportTicketPayload): Observable<any> {
    const payload: any = {
      subject: data.subject,
      description: data.description,
      priority: data.priority ?? 'MEDIUM',
    };
    if (data.client) {
      payload.client = data.client;
    }
    if (data.license) {
      payload.license = data.license;
    }
    return this.http.post(`${BASE_URL}/support-tickets/`, payload as SupportTicketPayload);
  }

  updateSupportTicket(id: number, data: Partial<SupportTicketPayload>): Observable<any> {
    return this.http.patch(`${BASE_URL}/support-tickets/${id}/`, data);
  }
}
