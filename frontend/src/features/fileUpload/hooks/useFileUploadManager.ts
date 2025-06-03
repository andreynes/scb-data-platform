// frontend/src/features/fileUpload/hooks/useFileUploadManager.ts
import { useState, useCallback } from 'react';
import type { RcFile } from 'antd/es/upload';
import { uploadFiles } from '../../../services/filesApi'; 
import type { FileUploadStatusSchema } from '../../../services/generated'; 

// ВОЗВРАЩАЕМ ОРИГИНАЛЬНОЕ ИМЯ ИНТЕРФЕЙСА
export interface UploadProgressInfo { 
    uid: string; 
    name: string;
    status: 'waiting' | 'uploading' | 'success' | 'error' | 'accepted'; 
    percent?: number;
    response?: FileUploadStatusSchema; 
    errorMessage?: string;
    file?: RcFile; 
}

export interface FileUploadManagerHookResult {
    uploads: UploadProgressInfo[]; 
    handleUploadStart: (selectedFiles: RcFile[]) => Promise<void>;
    clearCompletedUploads: () => void;
}

export const useFileUploadManager = (): FileUploadManagerHookResult => {
    const [uploads, setUploads] = useState<UploadProgressInfo[]>([]); 

    const updateUploadState = useCallback((uid: string, updates: Partial<UploadProgressInfo>) => {
        setUploads(prevUploads =>
            prevUploads.map(up => (up.uid === uid ? { ...up, ...updates } : up))
        );
    }, []);

    const handleUploadStart = useCallback(
        async (selectedFiles: RcFile[]) => {
            const newUploadsInitial: UploadProgressInfo[] = selectedFiles.map(file => ({
                uid: file.uid,
                name: file.name,
                status: 'waiting', 
                percent: 0,
                file: file, 
            }));

            setUploads(prev => [...newUploadsInitial, ...prev]);

            for (const uploadInfo of newUploadsInitial) {
                if (uploadInfo.file) {
                    updateUploadState(uploadInfo.uid, { status: 'uploading', percent: 0 });
                    try {
                        const responses = await uploadFiles([uploadInfo.file as File]); 
                        
                        if (responses && responses.length > 0) {
                            const apiResponse = responses[0];
                            updateUploadState(uploadInfo.uid, {
                                status: apiResponse.status === 'Error' ? 'error' : 'accepted',
                                response: apiResponse,
                                percent: 100, 
                                errorMessage: apiResponse.status === 'Error' ? apiResponse.error_message : undefined,
                            });
                        } else {
                            updateUploadState(uploadInfo.uid, {
                                status: 'error',
                                errorMessage: 'Неожиданный ответ от сервера при загрузке файла.',
                                percent: 100,
                            });
                        }
                    } catch (error: any) {
                        console.error(`Ошибка загрузки файла ${uploadInfo.name}:`, error);
                        const detailMessage = error.response?.data?.detail || error.message || 'Ошибка сети или сервера.';
                        updateUploadState(uploadInfo.uid, {
                            status: 'error',
                            errorMessage: detailMessage,
                            percent: 100,
                        });
                    }
                }
            }
        },
        [updateUploadState] 
    );

    const clearCompletedUploads = useCallback(() => {
        setUploads(prev =>
            prev.filter(up => up.status === 'waiting' || up.status === 'uploading')
        );
    }, []);

    return {
        uploads,
        handleUploadStart,
        clearCompletedUploads,
    };
};