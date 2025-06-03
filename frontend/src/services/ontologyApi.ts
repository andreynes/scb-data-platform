// frontend/src/services/ontologyApi.ts
import { OpenAPI } from './generated/core/OpenAPI'; 
import { OntologyService } from './generated/services/OntologyService'; 
import type { OntologySchema } from './generated/models/OntologySchema'; 

// OpenAPI.BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'; 

export const fetchOntologySchema = async (): Promise<OntologySchema> => {
    try {
        const schema = await OntologyService.getCurrentOntologySchemaApiV1OntologySchemaGet();
        return schema;
    } catch (error) {
        console.error("Error fetching ontology schema:", error);
        throw error; 
    }
};