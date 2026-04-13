import { ChangeEvent, useRef, useState } from "react";
import { deleteAllData, updateFromGsheets, uploadBackup } from "@/api/Data";
import { API_ENDPOINTS } from "@/api/ApiConfig";

export default function DataImport() {
    const [ loading, setLoading ] = useState(false);
    const [ message, setMessage ] = useState<string | null>(null);
    const [ error, setError ] = useState<string | null>(null);
    const fileInputRef = useRef<HTMLInputElement | null>(null);

    const handleOperation = async (operation: () => Promise<void>, successText: string) => {
        setLoading(true);
        setMessage(null);
        setError(null);

        try {
            await operation();
            setMessage(successText);
        } catch (e) {
            setError((e as Error).message || "Произошла ошибка");
        } finally {
            setLoading(false);
        }
    };

    const handleUpdateFromGsheets = async () => {
        await handleOperation(
            async () => updateFromGsheets(),
            "Обновление данных из Google Sheets выполнено.",
        );
    };

    const handleDeleteAllData = async () => {
        await handleOperation(
            async () => deleteAllData(),
            "Все данные успешно удалены.",
        );
    };

    const handleCreateBackup = () => window.open(API_ENDPOINTS.DATA.DB, "_blank");

    const handleUploadBackup = () => fileInputRef.current?.click();

    const handleFileSelected = async (event: ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (!file)
            return;

        await handleOperation(
            async () => uploadBackup(file),
            "Резервная копия успешно загружена.",
        );

        event.target.value = "";
    };

    const handleHardUpdate = async () => {
        setLoading(true);
        setMessage(null);
        setError(null);

        try {
            window.open(API_ENDPOINTS.DATA.DB, "_blank");
            await deleteAllData();
            await updateFromGsheets();
            setMessage("Hard update выполнен: резервная копия создана, данные удалены, данные обновлены.");
        } catch (e) {
            setError((e as Error).message || "Произошла ошибка при жестком обновлении.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="data-import-page">
            <h1>Загрузка данных</h1>

            <div className="button-group">
                <button type="button" onClick={ handleUpdateFromGsheets } disabled={ loading }>
                    Обновить из Google Sheets
                </button>
                <button type="button" onClick={ handleDeleteAllData } disabled={ loading }>
                    Удалить все данные
                </button>
                <button type="button" onClick={ handleCreateBackup } disabled={ loading }>
                    Создать резервную копию
                </button>
                <button type="button" onClick={ handleUploadBackup } disabled={ loading }>
                    Загрузить резервную копию
                </button>
                <button type="button" onClick={ handleHardUpdate } disabled={ loading }>
                    Hard update
                </button>
            </div>

            {message && <div className="message success">{message}</div>}
            {error && <div className="message error">{error}</div>}

            <input
                ref={ fileInputRef }
                type="file"
                style={ { display: "none" } }
                onChange={ handleFileSelected }
                accept="*/*"
            />
        </div>
    );
}
