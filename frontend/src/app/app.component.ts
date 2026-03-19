import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService, LicenseGenerateRequest, LicenseValidateByKeyRequest, SupportTicketPayload } from './api.service';
import { AuthService, UserInfo } from './auth.service';

type Section =
  | 'home'
  | 'generate'
  | 'validate'
  | 'clients'
  | 'products'
  | 'license-types'
  | 'licenses'
  | 'tickets'
  | 'users'
  | 'help';

/** Форма генерации: id могут быть не выбраны (null). */
interface GenerateFormPayload {
  client_id: number | null;
  product_id: number | null;
  license_type_id: number | null;
  order_id?: number;
  max_activations?: number;
}

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent implements OnInit {
  section: Section = 'home';

  loggedIn = false;
  userInfo: UserInfo | null = null;
  loginUsername = '';
  loginPassword = '';
  loginError = '';
  loginLoading = false;
  showRegister = false;
  registerUsername = '';
  registerPassword = '';
  registerEmail = '';
  registerError = '';
  registerLoading = false;

  copySuccess: string | null = null;

  generatePayload: GenerateFormPayload = {
    client_id: null,
    product_id: null,
    license_type_id: null,
  };
  generatedLicense: any = null;
  validatePayload: LicenseValidateByKeyRequest = {
    key: '',
    device_id: 'DEVICE-1',
    device_name: 'My Device',
  };
  validationResult: any = null;

  clients: any[] = [];
  products: any[] = [];
  licenseTypes: any[] = [];
  licenses: any[] = [];
  supportTickets: any[] = [];
  users: { id: number; username: string; is_staff: boolean }[] = [];
  /** Для админа: выбранный пользователь, чьи данные показывать (null = не выбрано). */
  selectedOwnerId: number | null = null;

  loadingGenerate = false;
  loadingValidate = false;
  loadingList: Record<string, boolean> = {};
  errorMessage = '';

  newClient: { name: string; client_type: string; contact_email: string; contact_phone?: string; country?: string } = {
    name: '',
    client_type: 'COMPANY',
    contact_email: '',
  };
  editingClientId: number | null = null;
  newProduct: { name: string; code: string } = { name: '', code: '' };
  editingProductId: number | null = null;
  editingLicenseTypeId: number | null = null;
  newLicenseType: { name: string; description: string; max_devices: number; has_expiration: boolean; duration_days: number | null } = {
    name: '',
    description: '',
    max_devices: 1,
    has_expiration: true,
    duration_days: 30,
  };
  creating: Record<string, boolean> = {};

  newTicket: { client: number | null; license: number | null; subject: string; description: string; priority: 'LOW' | 'MEDIUM' | 'HIGH' } =
    {
      client: null,
      license: null,
      subject: '',
      description: '',
      priority: 'MEDIUM',
    };

  constructor(
    private api: ApiService,
    private auth: AuthService,
  ) {}

  ngOnInit() {
    if (this.auth.isLoggedIn()) {
      this.auth.getCurrentUser().subscribe((user) => {
        this.userInfo = user;
        this.loggedIn = !!user;
      });
    }
  }

  get isStaff(): boolean {
    return !!this.userInfo?.is_staff;
  }

  onLogin() {
    this.loginError = '';
    this.loginLoading = true;
    this.auth.login(this.loginUsername, this.loginPassword).subscribe({
      next: () => {
        this.auth.getCurrentUser().subscribe((user) => {
          this.userInfo = user;
          this.loggedIn = !!user;
          this.loginLoading = false;
        });
      },
      error: (err) => {
        if (err?.status === 0) {
          this.loginError = 'Сервер недоступен. Запустите backend на http://127.0.0.1:8000/';
        } else {
          this.loginError =
            err?.error?.non_field_errors?.[0] ||
            err?.error?.detail ||
            `Ошибка входа (HTTP ${err?.status ?? '—'})`;
        }
        this.loginLoading = false;
      },
    });
  }

  onLogout() {
    this.auth.logout();
    this.loggedIn = false;
    this.userInfo = null;
  }

  onRegister() {
    this.registerError = '';
    this.registerLoading = true;
    this.auth.register(this.registerUsername, this.registerPassword, this.registerEmail || undefined).subscribe({
      next: () => {
        this.auth.getCurrentUser().subscribe((user) => {
          this.userInfo = user;
          this.loggedIn = !!user;
          this.registerLoading = false;
          this.showRegister = false;
        });
      },
      error: (err) => {
        this.registerError = err?.error?.detail || err?.error?.username?.[0] || 'Ошибка регистрации';
        this.registerLoading = false;
      },
    });
  }

  copyKey(text: string, id?: string) {
    const key = id ?? text?.slice(0, 12) ?? '';
    if (!text) return;
    navigator.clipboard.writeText(text).then(
      () => {
        this.copySuccess = key;
        setTimeout(() => (this.copySuccess = null), 2000);
      },
      () => {}
    );
  }

  setSection(s: Section) {
    this.section = s;
    this.errorMessage = '';
    const ownerId = this.isStaff ? this.selectedOwnerId : undefined;
    if (s === 'home') { /* только приветствие */ }
    if (s === 'generate') {
      if (this.isStaff) this.loadUsers();
      this.loadClients(ownerId);
      this.loadProducts(ownerId);
      this.loadLicenseTypes(ownerId);
    }
    if (s === 'validate') { /* форма без загрузки */ }
    if (s === 'clients') { if (this.isStaff) this.loadUsers(); this.loadClients(ownerId); }
    if (s === 'products') { if (this.isStaff) this.loadUsers(); this.loadProducts(ownerId); }
    if (s === 'license-types') { if (this.isStaff) this.loadUsers(); this.loadLicenseTypes(ownerId); }
    if (s === 'licenses') { if (this.isStaff) this.loadUsers(); this.loadLicenses(ownerId); }
    if (s === 'tickets') {
      if (this.isStaff) this.loadUsers();
      this.loadClients(ownerId);
      this.loadLicenses(ownerId);
      this.loadSupportTickets();
    }
    if (s === 'users') this.loadUsers();
  }

  setSelectedOwnerAndReload(ownerId: number | null) {
    this.selectedOwnerId = ownerId;
    const s = this.section;
    const id = this.isStaff ? this.selectedOwnerId : undefined;
    if (s === 'generate') {
      this.loadClients(id);
      this.loadProducts(id);
      this.loadLicenseTypes(id);
    }
    if (s === 'clients') this.loadClients(id);
    if (s === 'products') this.loadProducts(id);
    if (s === 'license-types') this.loadLicenseTypes(id);
    if (s === 'licenses') this.loadLicenses(id);
    if (s === 'tickets') {
      this.loadClients(id);
      this.loadLicenses(id);
      this.loadSupportTickets();
    }
  }

  loadUsers() {
    this.loadingList['users'] = true;
    this.api.getUsers().subscribe({
      next: (data) => {
        this.users = Array.isArray(data) ? data : [];
        this.loadingList['users'] = false;
      },
      error: (err) => {
        this.handleApiError(err);
        this.errorMessage = 'Не удалось загрузить список пользователей';
        this.loadingList['users'] = false;
      },
    });
  }

  private handleApiError(err: any) {
    if (err?.status === 401) {
      this.auth.logout();
      this.loggedIn = false;
      this.userInfo = null;
    }
  }

  loadClients(ownerId?: number | null) {
    this.loadingList['clients'] = true;
    this.api.getClients(ownerId).subscribe({
      next: (data) => {
        this.clients = Array.isArray(data) ? data : (data as any)?.results ?? [];
        this.loadingList['clients'] = false;
      },
      error: (err) => {
        this.handleApiError(err);
        this.errorMessage = 'Не удалось загрузить клиентов';
        this.loadingList['clients'] = false;
      },
    });
  }

  loadProducts(ownerId?: number | null) {
    this.loadingList['products'] = true;
    this.api.getProducts(ownerId).subscribe({
      next: (data) => {
        this.products = Array.isArray(data) ? data : (data as any)?.results ?? [];
        this.loadingList['products'] = false;
      },
      error: (err) => {
        this.handleApiError(err);
        this.errorMessage = 'Не удалось загрузить продукты';
        this.loadingList['products'] = false;
      },
    });
  }

  loadLicenseTypes(ownerId?: number | null) {
    this.loadingList['license-types'] = true;
    this.api.getLicenseTypes(ownerId).subscribe({
      next: (data) => {
        this.licenseTypes = Array.isArray(data) ? data : (data as any)?.results ?? [];
        this.loadingList['license-types'] = false;
      },
      error: (err) => {
        this.handleApiError(err);
        this.errorMessage = 'Не удалось загрузить типы лицензий';
        this.loadingList['license-types'] = false;
      },
    });
  }

  loadLicenses(ownerId?: number | null) {
    this.loadingList['licenses'] = true;
    this.api.getLicenses(ownerId).subscribe({
      next: (data) => {
        this.licenses = Array.isArray(data) ? data : (data as any)?.results ?? [];
        this.loadingList['licenses'] = false;
      },
      error: (err) => {
        this.handleApiError(err);
        this.errorMessage = 'Не удалось загрузить лицензии';
        this.loadingList['licenses'] = false;
      },
    });
  }

  loadSupportTickets() {
    this.loadingList['tickets'] = true;
    this.api.getSupportTickets().subscribe({
      next: (data) => {
        this.supportTickets = Array.isArray(data) ? data : (data as any)?.results ?? [];
        this.loadingList['tickets'] = false;
      },
      error: (err) => {
        this.handleApiError(err);
        this.errorMessage = 'Не удалось загрузить тикеты поддержки';
        this.loadingList['tickets'] = false;
      },
    });
  }

  onGenerate() {
    const { client_id, product_id, license_type_id } = this.generatePayload;
    if (client_id == null || product_id == null || license_type_id == null) {
      this.errorMessage = 'Выберите клиента, продукт и тип лицензии';
      return;
    }
    this.errorMessage = '';
    this.loadingGenerate = true;
    this.api.generateLicense({ ...this.generatePayload, client_id, product_id, license_type_id }).subscribe({
      next: (res) => {
        this.generatedLicense = res;
        this.validatePayload.key = res.key ?? '';
        this.loadingGenerate = false;
        this.loadLicenses(this.isStaff ? this.selectedOwnerId : undefined);
      },
      error: (err) => {
        this.handleApiError(err);
        this.errorMessage = err?.error?.detail || 'Ошибка генерации лицензии';
        this.loadingGenerate = false;
      },
    });
  }

  onValidate() {
    this.errorMessage = '';
    this.loadingValidate = true;
    this.api.validateLicenseByKey(this.validatePayload).subscribe({
      next: (res) => {
        this.validationResult = res;
        this.loadingValidate = false;
      },
      error: (err) => {
        this.handleApiError(err);
        this.errorMessage = err?.error?.detail || 'Ошибка проверки лицензии';
        this.loadingValidate = false;
      },
    });
  }

  onRenewLicense(licenseId: number) {
    this.errorMessage = '';
    this.api.renewLicense(licenseId).subscribe({
      next: () => {
        this.loadLicenses(this.isStaff ? this.selectedOwnerId : undefined);
      },
      error: (err) => {
        this.errorMessage = err?.error?.detail || 'Не удалось продлить лицензию';
      },
    });
  }

  onSaveClient() {
    this.errorMessage = '';
    this.creating['client'] = true;

    const done = () => {
      this.creating['client'] = false;
      this.editingClientId = null;
      this.newClient = { name: '', client_type: 'COMPANY', contact_email: '' };
      this.loadClients(this.isStaff ? this.selectedOwnerId : undefined);
    };

    if (this.editingClientId == null) {
      this.api.createClient(this.newClient).subscribe({
        next: () => done(),
        error: (err) => {
          this.creating['client'] = false;
          this.errorMessage =
            err?.error?.name?.[0] || err?.error?.contact_email?.[0] || 'Ошибка создания клиента';
        },
      });
    } else {
      this.api.updateClient(this.editingClientId, this.newClient).subscribe({
        next: () => done(),
        error: (err) => {
          this.creating['client'] = false;
          this.errorMessage =
            err?.error?.name?.[0] || err?.error?.contact_email?.[0] || 'Ошибка обновления клиента';
        },
      });
    }
  }

  onEditClient(c: any) {
    this.editingClientId = c.id;
    this.newClient = {
      name: c.name,
      client_type: c.client_type,
      contact_email: c.contact_email,
      contact_phone: c.contact_phone,
      country: c.country,
    };
  }

  onDeleteClient(id: number) {
    if (!confirm('Удалить клиента?')) {
      return;
    }
    this.errorMessage = '';
    this.api.deleteClient(id).subscribe({
      next: () => {
        this.loadClients(this.isStaff ? this.selectedOwnerId : undefined);
      },
      error: (err) => {
        this.errorMessage = err?.error?.detail || 'Не удалось удалить клиента';
      },
    });
  }

  onSaveProduct() {
    this.errorMessage = '';
    this.creating['product'] = true;

    const done = () => {
      this.creating['product'] = false;
      this.editingProductId = null;
      this.newProduct = { name: '', code: '' };
      this.loadProducts(this.isStaff ? this.selectedOwnerId : undefined);
    };

    if (this.editingProductId == null) {
      this.api.createProduct(this.newProduct).subscribe({
        next: () => done(),
        error: (err) => {
          this.creating['product'] = false;
          this.errorMessage =
            err?.error?.code?.[0] || err?.error?.name?.[0] || 'Ошибка создания продукта (код должен быть уникальным)';
        },
      });
    } else {
      this.api.updateProduct(this.editingProductId, this.newProduct).subscribe({
        next: () => done(),
        error: (err) => {
          this.creating['product'] = false;
          this.errorMessage =
            err?.error?.code?.[0] || err?.error?.name?.[0] || 'Ошибка обновления продукта (код должен быть уникальным)';
        },
      });
    }
  }

  onEditProduct(p: any) {
    this.editingProductId = p.id;
    this.newProduct = { name: p.name, code: p.code };
  }

  onDeleteProduct(id: number) {
    if (!confirm('Удалить продукт?')) {
      return;
    }
    this.errorMessage = '';
    this.api.deleteProduct(id).subscribe({
      next: () => {
        this.loadProducts(this.isStaff ? this.selectedOwnerId : undefined);
      },
      error: (err) => {
        this.errorMessage = err?.error?.detail || 'Не удалось удалить продукт';
      },
    });
  }

  onSaveLicenseType() {
    this.errorMessage = '';
    this.creating['licenseType'] = true;

    const payload = {
      name: this.newLicenseType.name,
      description: this.newLicenseType.description || undefined,
      max_devices: this.newLicenseType.max_devices,
      has_expiration: this.newLicenseType.has_expiration,
      duration_days:
        this.newLicenseType.has_expiration && this.newLicenseType.duration_days != null
          ? this.newLicenseType.duration_days
          : undefined,
      renewable: true,
    };

    const done = () => {
      this.creating['licenseType'] = false;
      this.editingLicenseTypeId = null;
      this.newLicenseType = { name: '', description: '', max_devices: 1, has_expiration: true, duration_days: 30 };
      this.loadLicenseTypes(this.isStaff ? this.selectedOwnerId : undefined);
    };

    if (this.editingLicenseTypeId == null) {
      this.api.createLicenseType(payload).subscribe({
        next: () => done(),
        error: (err) => {
          this.creating['licenseType'] = false;
          this.errorMessage = err?.error?.name?.[0] || 'Ошибка создания типа лицензии';
        },
      });
    } else {
      const id = this.editingLicenseTypeId as number;
      this.api.updateLicenseType(id, payload).subscribe({
        next: () => done(),
        error: (err) => {
          this.creating['licenseType'] = false;
          this.errorMessage = err?.error?.name?.[0] || 'Ошибка обновления типа лицензии';
        },
      });
    }
  }

  onEditLicenseType(lt: any) {
    this.editingLicenseTypeId = lt.id;
    this.newLicenseType = {
      name: lt.name,
      description: lt.description,
      max_devices: lt.max_devices,
      has_expiration: lt.has_expiration,
      duration_days: lt.duration_days,
    };
  }

  onDeleteLicenseType(id: number) {
    if (!confirm('Удалить тип лицензии?')) {
      return;
    }
    this.errorMessage = '';
    this.api.deleteLicenseType(id).subscribe({
      next: () => {
        this.loadLicenseTypes(this.isStaff ? this.selectedOwnerId : undefined);
      },
      error: (err) => {
        this.errorMessage = err?.error?.detail || 'Не удалось удалить тип лицензии';
      },
    });
  }

  onDeleteLicense(id: number) {
    if (!confirm('Удалить лицензию (ключ)?')) {
      return;
    }
    this.errorMessage = '';
    this.api.deleteLicense(id).subscribe({
      next: () => {
        this.loadLicenses(this.isStaff ? this.selectedOwnerId : undefined);
      },
      error: (err) => {
        this.errorMessage = err?.error?.detail || 'Не удалось удалить лицензию';
      },
    });
  }

  onCreateTicket() {
    this.errorMessage = '';
    if (!this.newTicket.client) {
      this.errorMessage = 'Выберите клиента для тикета';
      return;
    }
    if (!this.newTicket.subject || !this.newTicket.description) {
      this.errorMessage = 'Заполните тему и описание тикета';
      return;
    }
    this.creating['ticket'] = true;
    const payload: SupportTicketPayload = {
      client: this.newTicket.client,
      license: this.newTicket.license ?? undefined,
      subject: this.newTicket.subject,
      description: this.newTicket.description,
      priority: this.newTicket.priority,
    };
    this.api.createSupportTicket(payload).subscribe({
      next: () => {
        this.creating['ticket'] = false;
        this.newTicket = { client: null, license: null, subject: '', description: '', priority: 'MEDIUM' };
        this.loadSupportTickets();
      },
      error: (err) => {
        this.creating['ticket'] = false;
        this.errorMessage =
          err?.error?.detail ||
          err?.error?.client?.[0] ||
          err?.error?.subject?.[0] ||
          err?.error?.description?.[0] ||
          err?.error?.non_field_errors?.[0] ||
          'Не удалось создать тикет';
      },
    });
  }

  onAdminSetTicketStatus(ticket: any, status: 'OPEN' | 'IN_PROGRESS' | 'RESOLVED' | 'CLOSED') {
    if (!this.isStaff) {
      return;
    }
    this.api.updateSupportTicket(ticket.id, { status }).subscribe({
      next: () => this.loadSupportTickets(),
      error: (err) => {
        this.errorMessage = err?.error?.detail || 'Не удалось обновить статус тикета';
      },
    });
  }

  onAdminAssignTicketToMe(ticket: any) {
    if (!this.isStaff || !this.userInfo?.id) {
      return;
    }
    this.api.updateSupportTicket(ticket.id, { assigned_to: this.userInfo.id }).subscribe({
      next: () => this.loadSupportTickets(),
      error: (err) => {
        this.errorMessage = err?.error?.detail || 'Не удалось назначить тикет';
      },
    });
  }
}
