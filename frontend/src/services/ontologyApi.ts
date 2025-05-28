// frontend/src/services/ontologyApi.ts (пример)
import { OpenAPI, OntologyService, OntologySchema } from './generated'; // Пути могут отличаться

// Возможно, нужно настроить OpenAPI.BASE, если он не берется из process.env
// OpenAPI.BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'; 

export const fetchOntologySchema = async (): Promise<OntologySchema> => {
    try {
        // Имя функции может отличаться в зависимости от вашего operationId в OpenAPI
        const schema = await OntologyService.getCurrentOntologySchemaApiV1OntologySchemaGet();
        return schema;
    } catch (error) {
        console.error("Error fetching ontology schema:", error);
        throw error; // Пробрасываем ошибку для обработки в Redux slice/хуке
    }
};