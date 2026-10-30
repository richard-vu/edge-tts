export interface ApiResponse<T> {
  success: boolean;
  code: string;
  message: string;
  timestamp: string;
  data?: T;
  errors?: Array<{
    [key: string]: unknown;
  }>;
}

export interface PageResponse<T> {
  content: T[];
  pageNo: number;
  pageSize: number;
  totalElements: number;
  totalPages: number;
}
