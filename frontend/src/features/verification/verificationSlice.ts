import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import * as adminApi from '../../services/adminApi';
import {
  VerificationDataSchema,
  VerificationResultSchema,
  VerificationTaskSchema,
  // Убедитесь, что эти типы экспортируются из './generated'
  // Если нет, их нужно будет определить здесь или в другом месте
  // type CorrectionInfo,
  // type VerificationStatus,
} from '../../services/generated';

// Если этих типов нет в generated, определим их здесь как заглушки
// Вам нужно будет заменить их на реальные типы из ваших схем
type CorrectionInfo = any;
type VerificationStatus = 'Verified' | 'NeedsFixing';


interface VerificationState {
  queueTasks: VerificationTaskSchema[];
  queueStatus: 'idle' | 'loading' | 'succeeded' | 'failed';
  queueError: string | null;
  
  currentTaskId: string | null;
  currentTaskData: VerificationDataSchema | null;
  taskStatus: 'idle' | 'loading' | 'succeeded' | 'failed';
  taskError: string | null;

  appliedCorrections: CorrectionInfo[];

  submitStatus: 'idle' | 'pending' | 'succeeded' | 'failed';
  submitError: string | null;
}

const initialState: VerificationState = {
  queueTasks: [],
  queueStatus: 'idle',
  queueError: null,
  currentTaskId: null,
  currentTaskData: null,
  taskStatus: 'idle',
  taskError: null,
  appliedCorrections: [],
  submitStatus: 'idle',
  submitError: null,
};

// Асинхронные Thunks
export const fetchVerificationQueueThunk = createAsyncThunk<
  VerificationTaskSchema[],
  { limit?: number; offset?: number } | void,
  { rejectValue: string }
>(
  'verification/fetchQueue',
  async (params, { rejectWithValue }) => {
    const { limit, offset } = params || {};
    try {
      return await adminApi.fetchVerificationQueue(limit, offset);
    } catch (error: any) {
      const message = error.response?.data?.detail || error.message || 'Failed to fetch verification queue';
      return rejectWithValue(message);
    }
  }
);

export const fetchVerificationTaskDataThunk = createAsyncThunk<
  VerificationDataSchema,
  string,
  { rejectValue: string }
>(
  'verification/fetchTaskData',
  async (taskId, { dispatch, rejectWithValue }) => {
    try {
      dispatch(clearCorrectionsAction());
      return await adminApi.fetchVerificationTaskData(taskId);
    } catch (error: any) {
      const message = error.response?.data?.detail || error.message || 'Failed to fetch task data';
      return rejectWithValue(message);
    }
  }
);

export const submitVerificationResultThunk = createAsyncThunk<
  void,
  VerificationResultSchema,
  { rejectValue: string }
>(
  'verification/submitResult',
  async (resultData, { dispatch, rejectWithValue }) => {
    try {
      await adminApi.submitVerificationResult(resultData);
      dispatch(clearCurrentVerificationTask());
      dispatch(clearCorrectionsAction());
    } catch (error: any) {
      const message = error.response?.data?.detail || error.message || 'Failed to submit verification result';
      return rejectWithValue(message);
    }
  }
);

const verificationSlice = createSlice({
  name: 'verification',
  initialState,
  reducers: {
    setSelectedTaskId: (state, action: PayloadAction<string | null>) => {
      state.currentTaskId = action.payload;
      if (!action.payload) {
        state.currentTaskData = null;
        state.taskStatus = 'idle';
        state.taskError = null;
        state.appliedCorrections = [];
      }
    },
    clearCurrentVerificationTask: (state) => {
        state.currentTaskId = null;
        state.currentTaskData = null;
        state.taskStatus = 'idle';
        state.taskError = null;
    },
    addOrUpdateCorrectionAction: (state, action: PayloadAction<CorrectionInfo>) => {
        const index = state.appliedCorrections.findIndex((c: any) => c.atomId === action.payload.atomId && c.field === action.payload.field);
        if (index !== -1) {
            state.appliedCorrections[index] = action.payload;
        } else {
            state.appliedCorrections.push(action.payload);
        }
    },
    clearCorrectionsAction: (state) => {
        state.appliedCorrections = [];
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchVerificationQueueThunk.pending, (state) => {
        state.queueStatus = 'loading';
        state.queueError = null;
      })
      .addCase(fetchVerificationQueueThunk.fulfilled, (state, action) => {
        state.queueStatus = 'succeeded';
        state.queueTasks = action.payload;
      })
      .addCase(fetchVerificationQueueThunk.rejected, (state, action) => {
        state.queueStatus = 'failed';
        state.queueError = action.payload ?? 'Unknown error fetching queue';
      })
      .addCase(fetchVerificationTaskDataThunk.pending, (state, action) => {
        state.taskStatus = 'loading';
        state.taskError = null;
        state.currentTaskData = null;
      })
      .addCase(fetchVerificationTaskDataThunk.fulfilled, (state, action) => {
        state.taskStatus = 'succeeded';
        state.currentTaskData = action.payload;
      })
      .addCase(fetchVerificationTaskDataThunk.rejected, (state, action) => {
        state.taskStatus = 'failed';
        state.taskError = action.payload ?? 'Unknown error fetching task data';
      })
      .addCase(submitVerificationResultThunk.pending, (state) => {
        state.submitStatus = 'pending';
        state.submitError = null;
      })
      .addCase(submitVerificationResultThunk.fulfilled, (state) => {
        state.submitStatus = 'succeeded';
      })
      .addCase(submitVerificationResultThunk.rejected, (state, action) => {
        state.submitStatus = 'failed';
        state.submitError = action.payload ?? 'Unknown error';
      });
  },
});

export const {
  setSelectedTaskId,
  clearCurrentVerificationTask,
  addOrUpdateCorrectionAction,
  clearCorrectionsAction,
} = verificationSlice.actions;

// --- ИСПРАВЛЕНО: Добавлены недостающие селекторы ---
export const selectVerificationQueueTasks = (state: { verification: VerificationState }) => state.verification.queueTasks;
export const selectVerificationQueueIsLoading = (state: { verification: VerificationState }) => state.verification.queueStatus === 'loading';
export const selectVerificationQueueError = (state: { verification: VerificationState }) => state.verification.queueError;
export const selectCurrentVerificationTaskData = (state: { verification: VerificationState }) => state.verification.currentTaskData;
// Добавляем селекторы, которых не хватало
export const selectCurrentVerificationTaskStatus = (state: { verification: VerificationState }) => state.verification.taskStatus;
export const selectCurrentVerificationTaskError = (state: { verification: VerificationState }) => state.verification.taskError;

export const selectVerificationSubmitStatus = (state: { verification: VerificationState }) => state.verification.submitStatus;
export const selectVerificationSubmitError = (state: { verification: VerificationState }) => state.verification.submitError;


export default verificationSlice.reducer;