import os
import requests
import base64
import json

from google.adk.tools import ToolContext

from typing import Dict, List, Optional, Any
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# Azure DevOps Configuration - Global Variables from .env file
AZURE_DEVOPS_ORGANIZATION = os.getenv("AZURE_DEVOPS_ORGANIZATION", "your-organization")
AZURE_DEVOPS_PROJECT = os.getenv("AZURE_DEVOPS_PROJECT", "your-project")
AZURE_DEVOPS_PAT = os.getenv("AZURE_DEVOPS_PAT", "your-pat-token")
AZURE_DEVOPS_USER_EMAIL = os.getenv("AZURE_DEVOPS_USER_EMAIL", "your-email@company.com")


def get_azure_devops_headers() -> Dict[str, str]:
    """
    Get headers with authentication for Azure DevOps API requests

    Returns:
        Dictionary with headers including authentication
    """
    # Encode PAT for basic authentication
    auth_string = f":{AZURE_DEVOPS_PAT}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()

    return {
        "Authorization": f"Basic {encoded_auth}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }


def get_azure_devops_base_url() -> str:
    """
    Get the base URL for Azure DevOps API

    Returns:
        Base URL string
    """
    return f"https://dev.azure.com/{AZURE_DEVOPS_ORGANIZATION}"


def get_tickets_assigned_to_me(tool_context: ToolContext, state: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get all work items assigned to the configured user, acotados al proyecto definido en AZURE_DEVOPS_PROJECT.

    Args:
        state: Optional state filter (e.g., "New", "In Progress"). If None, no state filter is applied.

    Returns:
        List of work items assigned to the user en el proyecto actual
    """
    
    if state:
        state_filter = f"AND [System.State] = '{state}'"
    else:
        state_filter = " AND [System.State] <> 'Closed' AND [System.State] <> 'Removed' "

    try:
        base_url = get_azure_devops_base_url()
        headers = get_azure_devops_headers()
        # WIQL query con filtro explícito de proyecto
        wiql_query = {
            "query": f"""
            SELECT [System.Id], [System.Title], [System.State], [System.WorkItemType],
                   [System.AssignedTo], [System.CreatedDate], [System.ChangedDate], [System.TeamProject]
            FROM WorkItems
            WHERE [System.AssignedTo] = '{AZURE_DEVOPS_USER_EMAIL}'
            AND [System.TeamProject] = '{AZURE_DEVOPS_PROJECT}'
            {state_filter}
            ORDER BY [System.ChangedDate] DESC
            """
        }
        url = f"{base_url}/{AZURE_DEVOPS_PROJECT}/_apis/wit/wiql?api-version=7.0"
        response = requests.post(url, headers=headers, json=wiql_query)
        response.raise_for_status()
        wiql_result = response.json()
        work_items = []
        # Get detailed information for each work item
        if wiql_result.get("workItems"):
            ids = [str(item["id"]) for item in wiql_result["workItems"]]
            if ids:
                details_url = f"{base_url}/{AZURE_DEVOPS_PROJECT}/_apis/wit/workitems?ids={','.join(ids)}&api-version=7.0"
                details_response = requests.get(details_url, headers=headers)
                details_response.raise_for_status()
                work_items = details_response.json().get("value", [])
        return work_items
    except requests.exceptions.RequestException as e:
        print(f"Error fetching assigned tickets: {e}")
        return []


def get_work_item_details(work_item_id: int) -> Optional[Dict[str, Any]]:
    """
    Get detailed information about a specific work item

    Args:
        work_item_id: ID of the work item

    Returns:
        Work item details or None if not found
    """
    try:
        base_url = get_azure_devops_base_url()
        headers = get_azure_devops_headers()

        url = f"{base_url}/{AZURE_DEVOPS_PROJECT}/_apis/wit/workitems/{work_item_id}?$expand=all&api-version=7.0"
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"Error fetching work item {work_item_id}: {e}")
        return None


def update_ticket_description(work_item_id: int, new_description_markdown: str) -> bool:
    """
    Update the description of a work item

    Args:
        work_item_id: ID of the work item
        new_description: New description text

    Returns:
        True if successful, False otherwise
    """
    try:
        base_url = get_azure_devops_base_url()
        headers = get_azure_devops_headers()

        # Azure DevOps uses PATCH operations with JSON Patch format
        patch_document = [
            {
                "op": "replace",
                "path": "/fields/System.Description",
                "value": new_description_markdown
            },
            {
                "op": "add",
                "path": "/multilineFieldsFormat/System.Description",
                "value": "Markdown"
            },
        ]

        url = f"{base_url}/{AZURE_DEVOPS_PROJECT}/_apis/wit/workitems/{work_item_id}?api-version=7.0"
        headers["Content-Type"] = "application/json-patch+json"

        response = requests.patch(url, headers=headers, json=patch_document)
        response.raise_for_status()

        print(f"Successfully updated description for work item {work_item_id}")
        return True

    except requests.exceptions.RequestException as e:
        print(f"Error updating work item {work_item_id} description: {e}")
        return False


def add_comment_to_ticket(work_item_id: int, comment: str) -> bool:
    """
    Add a comment to a work item. El texto se sube como Markdown.

    Args:
        work_item_id: ID of the work item
        comment: Comment text to add (puede contener sintaxis Markdown)
    Returns:
        True if successful, False otherwise
    """
    try:
        base_url = get_azure_devops_base_url()
        headers = get_azure_devops_headers()
        # Procesar saltos de línea para Markdown: Azure DevOps requiere doble espacio antes de salto de línea para soft break, o doble salto para hard break.
        # Aquí convertimos cada salto de línea simple en doble espacio + salto de línea (soft break)
        processed_comment = comment.replace("\r\n", "\n")  # Normalizar saltos de línea
        processed_comment = processed_comment.replace("\n", "  \n")
        comment_data = {
            "text": processed_comment
        }
        print("comment", processed_comment)
        url = f"{base_url}/{AZURE_DEVOPS_PROJECT}/_apis/wit/workitems/{work_item_id}/comments?format=0&api-version=7.1-preview.4"
        headers["Content-Type"] = "application/json"
        response = requests.post(url, headers=headers, json=comment_data)
        response.raise_for_status()
        print(f"Successfully added markdown comment to work item {work_item_id}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error adding comment to work item {work_item_id}: {e}")
        return False


def download_attachment(attachment_id: str, file_name: str, download_path: str = ".") -> bool:
    """
    Download an attachment from a work item

    Args:
        attachment_id: ID of the attachment
        file_name: Name to save the file as
        download_path: Path to save the file (default: current directory)

    Returns:
        True if successful, False otherwise
    """
    try:
        base_url = get_azure_devops_base_url()
        headers = get_azure_devops_headers()

        url = f"{base_url}/_apis/wit/attachments/{attachment_id}?api-version=7.0"
        response = requests.get(url, headers=headers, stream=True)
        response.raise_for_status()

        file_path = os.path.join(download_path, file_name)

        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

        print(f"Successfully downloaded attachment to {file_path}")
        return True

    except requests.exceptions.RequestException as e:
        print(f"Error downloading attachment {attachment_id}: {e}")
        return False
    except IOError as e:
        print(f"Error saving file {file_name}: {e}")
        return False


def update_ticket_status(work_item_id: int, new_status: str) -> bool:
    """
    Update the status/state of a work item

    Args:
        work_item_id: ID of the work item
        new_status: New status (e.g., 'Active', 'Resolved', 'Closed', etc.)

    Returns:
        True if successful, False otherwise
    """
    try:
        base_url = get_azure_devops_base_url()
        headers = get_azure_devops_headers()

        patch_document = [
            {
                "op": "replace",
                "path": "/fields/System.State",
                "value": new_status
            }
        ]

        url = f"{base_url}/{AZURE_DEVOPS_PROJECT}/_apis/wit/workitems/{work_item_id}?api-version=7.0"
        headers["Content-Type"] = "application/json-patch+json"

        response = requests.patch(url, headers=headers, json=patch_document)
        response.raise_for_status()

        print(f"Successfully updated status of work item {work_item_id} to '{new_status}'")
        return True

    except requests.exceptions.RequestException as e:
        print(f"Error updating work item {work_item_id} status: {e}")
        return False


def get_work_item_attachments(work_item_id: int) -> List[Dict[str, Any]]:
    """
    Get list of attachments for a work item

    Args:
        work_item_id: ID of the work item

    Returns:
        List of attachment information
    """
    try:
        # Get work item details including relations (attachments)
        work_item = get_work_item_details(work_item_id)

        if not work_item:
            return []

        attachments = []
        relations = work_item.get("relations", [])

        for relation in relations:
            if relation.get("rel") == "AttachedFile":
                attachment_url = relation.get("url", "")
                # Extract attachment ID from URL
                if "/attachments/" in attachment_url:
                    attachment_id = attachment_url.split("/attachments/")[-1].split("?")[0]
                    attachment_info = {
                        "id": attachment_id,
                        "url": attachment_url,
                        "attributes": relation.get("attributes", {})
                    }
                    attachments.append(attachment_info)

        return attachments

    except Exception as e:
        print(f"Error getting attachments for work item {work_item_id}: {e}")
        return []


def create_ticket(title: str, description_in_markdown: Optional[str] = None, work_item_type: Optional[str] = "Task") -> Optional[Dict[str, Any]]:
    """
    Create a new work item/ticket with the specified title and type.

    Args:
        title: Title of the new work item
        work_item_type: Tipo de work item. Valores soportados: "Bug", "User Story", "Epic", "Task", "Feature". (Por defecto: "Task")
    Returns:
        Created work item details or None if creation failed
    """
    # Valores soportados por Azure DevOps: Bug, User Story, Epic, Task, Feature
    supported_types = {"Bug", "User Story", "Epic", "Task", "Feature"}
    if work_item_type not in supported_types:
        print(f"Error: work_item_type '{work_item_type}' no soportado. Valores válidos: {supported_types}")
        return None
    try:
        base_url = get_azure_devops_base_url()
        headers = get_azure_devops_headers()
        work_item_data = [
            {"op": "add", "path": "/fields/System.Title", "value": title},
            {"op": "add", "path": "/fields/System.AssignedTo", "value": AZURE_DEVOPS_USER_EMAIL},
            {"op": "add", "path": "/fields/System.State", "value": "New"}
        ]
        url = f"{base_url}/{AZURE_DEVOPS_PROJECT}/_apis/wit/workitems/${work_item_type}?api-version=7.0"
        headers["Content-Type"] = "application/json-patch+json"
        response = requests.post(url, headers=headers, json=work_item_data)
        response.raise_for_status()
        created_work_item = response.json()
        work_item_id = created_work_item.get("id")
        print(f"Successfully created work item {work_item_id} of type '{work_item_type}' with title: '{title}'")

        if description_in_markdown:
            update_ticket_description(work_item_id, description_in_markdown)

        return created_work_item
    except requests.exceptions.RequestException as e:
        print(f"Error creating work item with title '{title}': {e}")
        return None


def get_comments_from_ticket(work_item_id: int) -> Optional[list]:
    """
    Obtiene la lista de comentarios asociados a un work item/ticket de Azure DevOps.

    Args:
        work_item_id: ID del work item
    Returns:
        Lista de comentarios (cada uno como dict), o None si hay error
    """
    try:
        base_url = get_azure_devops_base_url()
        headers = get_azure_devops_headers()
        url = f"{base_url}/{AZURE_DEVOPS_PROJECT}/_apis/wit/workitems/{work_item_id}/comments?api-version=7.0-preview.3"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        # Los comentarios están en el campo 'comments' (lista de dicts)
        comments = data.get("comments", [])
        print(f"Se han recuperado {len(comments)} comentarios del work item {work_item_id}")
        return comments
    except requests.exceptions.RequestException as e:
        print(f"Error obteniendo comentarios del work item {work_item_id}: {e}")
        return None

def load_context(agentName : str) -> Dict[str, str]:
    """
    Carga el contexto específico para un agente desde la wiki de Azure DevOps.

    Args:
        agentName: Nombre del agente (que coincide con el nombre de la página en la wiki)
    Returns:
        Diccionario con 'description' e 'instruction', o vacío si hay error
    """
    context = {
        "description": "",
        "instruction": ""
    }

    agent_definition = get_wiki_page_content(agentName)

    # Validar que la página se haya recuperado correctamente
    if agent_definition is None:
        print(f"Error: No se pudo recuperar la definición del agente '{agentName}'.")
        return context

    # Aquí asumimos que la página tiene un formato específico para separar descripción e instrucciones
    # Por ejemplo, usando encabezados Markdown: ## Description y ## Instruction
    description_marker = "## Description"
    instruction_marker = "## Instruction"

    description_start = agent_definition.find(description_marker)

    instruction_start = agent_definition.find(instruction_marker)

    if description_start != -1 and instruction_start != -1:
        context["description"] = agent_definition[description_start + len(description_marker):instruction_start].strip()
        context["instruction"] = agent_definition[instruction_start + len(instruction_marker):].strip()
    elif description_start != -1:
        context["description"] = agent_definition[description_start + len(description_marker):].strip()
    elif instruction_start != -1:
        context["instruction"] = agent_definition[instruction_start + len(instruction_marker):].strip()
    else:
        print(f"Advertencia: No se encontraron secciones de descripción o instrucciones en la definición del agente '{agentName}'.")
    
    workflow_description = get_wiki_page_content("Management Workflows")
    if workflow_description:
        context["instruction"] += "\n\n" + workflow_description

    return context

def get_instructions(agentName : str) -> Optional[str]:
    """
    Recupera las instrucciones específicas para un agente desde la wiki de Azure DevOps.

    Args:
        agentName: Nombre del agente (que coincide con el nombre de la página en la wiki)
    Returns:
        Instrucciones como string, o None si hay error
    """
    workflow_description = get_wiki_page_content("Management Workflows")
    agent_definition = get_wiki_page_content(agentName)

    # Validar que ambas páginas se hayan recuperado correctamente
    if agent_definition is None and workflow_description is None:
        print(f"Error: No se pudo recuperar ni la definición del agente '{agentName}' ni el workflow de gestión.")
        return None
    elif agent_definition is None:
        print(f"Advertencia: No se pudo recuperar la definición del agente '{agentName}'. Usando solo workflow description.")
        return workflow_description
    elif workflow_description is None:
        print(f"Advertencia: No se pudo recuperar la descripción del workflow. Usando solo agent definition.")
        return agent_definition

    return agent_definition + "\n\n" + workflow_description


def get_wiki_page_content(page_path: str) -> Optional[str]:
    """
    Recupera el contenido de una página de la wiki asociada al proyecto Azure DevOps.

    Args:
        page_path: Ruta de la página dentro de la wiki (ejemplo: 'Home', 'docs/intro')
        wiki_name: Nombre de la wiki (si no se indica, se usa la primera wiki del proyecto)
    Returns:
        Contenido de la página como string, o None si hay error
    """

    wiki_name = "buildgentic.wiki"

    try:
        base_url = get_azure_devops_base_url()
        headers = get_azure_devops_headers()
        # Si no se indica wiki_name, obtenemos la primera wiki del proyecto
        if not wiki_name:
            wikis_url = f"{base_url}/_apis/wiki/wikis?api-version=7.0"
            wikis_response = requests.get(wikis_url, headers=headers)
            wikis_response.raise_for_status()
            wikis = wikis_response.json().get("value", [])
            if not wikis:
                print("No se encontró ninguna wiki asociada al proyecto.")
                return None
            wiki_name = wikis[0].get("name")
        # Recuperar el contenido de la página
        page_url = f"{base_url}/{AZURE_DEVOPS_PROJECT}/_apis/wiki/wikis/{wiki_name}/pages?path={page_path}&includeContent=true&api-version=7.0"
        page_response = requests.get(page_url, headers=headers)
        page_response.raise_for_status()
        page_data = page_response.json()
        content = page_data.get("content")
        if content is None:
            print(f"No se encontró contenido en la página '{page_path}' de la wiki '{wiki_name}'.")

        return content
    except requests.exceptions.RequestException as e:
        print(f"Error recuperando la página de la wiki: {e}")
        return None


def update_wiki_page_content(page_path: str, new_content: str, comment: Optional[str] = None) -> bool:
    """
    Actualiza el contenido de una página existente en la wiki de Azure DevOps.

    Args:
        page_path: Ruta de la página dentro de la wiki (ejemplo: 'Home', 'docs/intro')
        new_content: Nuevo contenido en formato Markdown para la página
        wiki_name: Nombre de la wiki (si no se indica, se usa la primera wiki del proyecto)
        comment: Comentario opcional para el cambio (se registra en el historial de versiones)
    Returns:
        True si la actualización fue exitosa, False en caso contrario
    """

    wiki_name = "CIC.wiki"

    try:
        base_url = get_azure_devops_base_url()
        headers = get_azure_devops_headers()

        # Si no se indica wiki_name, obtenemos la primera wiki del proyecto
        if not wiki_name:
            wikis_url = f"{base_url}/{AZURE_DEVOPS_PROJECT}/_apis/wiki/wikis?api-version=7.0"
            wikis_response = requests.get(wikis_url, headers=headers)
            wikis_response.raise_for_status()
            wikis = wikis_response.json().get("value", [])
            if not wikis:
                print("No se encontró ninguna wiki asociada al proyecto.")
                return False
            wiki_name = wikis[0].get("name")

        # Primero obtenemos la página actual para obtener su ETag (versión)
        print("primer acceso")
        page_url = f"{base_url}/{AZURE_DEVOPS_PROJECT}/_apis/wiki/wikis/{wiki_name}/pages?path={page_path}&includeContent=true&api-version=7.0"
        page_response = requests.get(page_url, headers=headers)
        page_response.raise_for_status()
        page_data = page_response.json()
        etag = page_response.headers['ETag']

        # Azure DevOps requiere el ETag para actualizaciones (control de concurrencia)
        #etag = page_data.get("eTag")
        #if not etag:
        #    print(f"No se pudo obtener el ETag de la página '{page_path}'.")
        #    return False

        # Preparar el payload para la actualización
        update_data = {
            "content": new_content
        }

        # Agregar el comentario si se proporciona
        if comment:
            update_data["comment"] = comment

        # Actualizar la página con PUT
        headers["If-Match"] = etag
        headers["Content-Type"] = "application/json"

        update_response = requests.put(page_url, headers=headers, json=update_data)
        update_response.raise_for_status()

        print(f"Successfully updated wiki page '{page_path}' in wiki '{wiki_name}'")
        return True

    except requests.exceptions.RequestException as e:
        print(f"Error actualizando la página de la wiki '{page_path}': {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status: {e.response.status_code}")
            print(f"Response body: {e.response.text}")
        return False


def add_related_work_item(work_item_id: int, related_work_item_id: int) -> bool:
    """
    Añade una relación de tipo "Related" entre dos work items.

    Args:
        work_item_id: ID del work item que será actualizado con la relación
        related_work_item_id: ID del work item que se añadirá como relacionado
    Returns:
        True si la relación se creó exitosamente, False en caso contrario
    """
    try:
        base_url = get_azure_devops_base_url()
        headers = get_azure_devops_headers()

        # Construir la URL del work item relacionado
        related_work_item_url = f"{base_url}/{AZURE_DEVOPS_PROJECT}/_apis/wit/workItems/{related_work_item_id}"

        # Azure DevOps usa JSON Patch para añadir relaciones
        patch_document = [
            {
                "op": "add",
                "path": "/relations/-",
                "value": {
                    "rel": "System.LinkTypes.Related",
                    "url": related_work_item_url,
                    "attributes": {
                        "comment": "Relación añadida automáticamente"
                    }
                }
            }
        ]

        url = f"{base_url}/{AZURE_DEVOPS_PROJECT}/_apis/wit/workitems/{work_item_id}?api-version=7.0"
        headers["Content-Type"] = "application/json-patch+json"

        response = requests.patch(url, headers=headers, json=patch_document)
        response.raise_for_status()

        print(f"Successfully added Related link between work item {work_item_id} and {related_work_item_id}")
        return True

    except requests.exceptions.RequestException as e:
        print(f"Error adding related work item link: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status: {e.response.status_code}")
            print(f"Response body: {e.response.text}")
        return False


def get_work_items_by_type(work_item_type: str) -> List[Dict[str, Any]]:
    """
    DEPRECATED: usa search_work_items_by_type.

    Conserva la firma original pero ahora devuelve los campos unificados:
    id, title, description, state, type, tags
    """
    print("[DEPRECATED] get_work_items_by_type -> usa search_work_items_by_type")
    return search_work_items_by_type(work_item_type=work_item_type)


def get_work_items_by_tags(
    tags: List[str],
    match: str = "any",
    work_item_type: Optional[str] = None,
    state: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    DEPRECATED: usa search_work_items_by_tags.

    Conserva la firma original pero ahora devuelve los campos unificados:
    id, title, description, state, type, tags
    """
    print("[DEPRECATED] get_work_items_by_tags -> usa search_work_items_by_tags")
    return search_work_items_by_tags(tags=tags, match=match, work_item_type=work_item_type, state=state)


# -----------------------
# Helpers privados (WIQL)
# -----------------------
def _escape_wiql_value(value: Optional[str]) -> str:
    return value.replace("'", "''") if value is not None else ""


def _chunk(lst: List[str], size: int) -> List[List[str]]:
    return [lst[i : i + size] for i in range(0, len(lst), size)]


def _build_state_clause(state: Optional[str]) -> str:
    if state:
        return f"AND [System.State] = '{_escape_wiql_value(state)}'"
    return "AND [System.State] <> 'Closed' AND [System.State] <> 'Removed'"


def _build_type_clause(work_item_type: Optional[str]) -> str:
    if work_item_type:
        return f"AND [System.WorkItemType] = '{_escape_wiql_value(work_item_type)}'"
    return ""


def _execute_wiql_for_ids(where_clause: str) -> List[str]:
    """Ejecuta una WIQL básica que devuelve IDs, limitando al proyecto actual."""
    base_url = get_azure_devops_base_url()
    headers = get_azure_devops_headers()
    wiql_query = {
        "query": f"""
        SELECT [System.Id]
        FROM WorkItems
        WHERE [System.TeamProject] = '{AZURE_DEVOPS_PROJECT}'
        {where_clause}
        ORDER BY [System.ChangedDate] DESC
        """
    }
    url = f"{base_url}/{AZURE_DEVOPS_PROJECT}/_apis/wit/wiql?api-version=7.0"
    response = requests.post(url, headers=headers, json=wiql_query)
    response.raise_for_status()
    wiql_result = response.json()
    return [str(item["id"]) for item in wiql_result.get("workItems", [])]


def _fetch_work_items_details(ids: List[str], fields: List[str]) -> List[Dict[str, Any]]:
    if not ids:
        return []
    base_url = get_azure_devops_base_url()
    headers = get_azure_devops_headers()
    field_param = ",".join(fields)
    all_items: List[Dict[str, Any]] = []
    for group in _chunk(ids, 200):
        details_url = (
            f"{base_url}/{AZURE_DEVOPS_PROJECT}/_apis/wit/workitems?ids={','.join(group)}&fields={field_param}&api-version=7.0"
        )
        details_response = requests.get(details_url, headers=headers)
        details_response.raise_for_status()
        all_items.extend(details_response.json().get("value", []))
    return all_items


def _format_work_item(item: Dict[str, Any]) -> Dict[str, Any]:
    flds = item.get("fields", {})
    return {
        "id": item.get("id"),
        "title": flds.get("System.Title", ""),
        "description": flds.get("System.Description", ""),
        "state": flds.get("System.State", ""),
        "type": flds.get("System.WorkItemType", ""),
        "tags": flds.get("System.Tags", ""),
    }


# -----------------------
# Nuevos métodos search_*
# -----------------------
def search_work_items_by_type(
    work_item_type: str,
    state: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Busca work items por tipo, devolviendo una estructura unificada:
    id, title, description, state, type, tags.
    """
    try:
        where_clause = " ".join([
            _build_type_clause(work_item_type),
            _build_state_clause(state),
        ])
        ids = _execute_wiql_for_ids(where_clause)
        fields = [
            "System.Id",
            "System.Title",
            "System.Description",
            "System.State",
            "System.WorkItemType",
            "System.Tags",
        ]
        items = _fetch_work_items_details(ids, fields)
        return [_format_work_item(it) for it in items]
    except requests.exceptions.RequestException as e:
        print(f"Error searching work items by type '{work_item_type}': {e}")
        return []


def search_work_items_by_tags(
    tags: List[str],
    match: str = "any",
    work_item_type: Optional[str] = None,
    state: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Busca work items por uno o varios tags, devolviendo una estructura unificada:
    id, title, description, state, type, tags.
    """
    try:
        if not tags:
            return []

        safe_tags = [_escape_wiql_value(t.strip()) for t in tags if t and t.strip()]
        if not safe_tags:
            return []

        # Construir predicado de tags
        if match.lower() == "all":
            tag_predicate = " AND ".join([f"[System.Tags] CONTAINS '{t}'" for t in safe_tags])
        else:
            tag_predicate = " OR ".join([f"[System.Tags] CONTAINS '{t}'" for t in safe_tags])
            tag_predicate = f"( {tag_predicate} )"

        where_clause = " ".join([
            _build_type_clause(work_item_type),
            _build_state_clause(state),
            f"AND {tag_predicate}",
        ])

        ids = _execute_wiql_for_ids(where_clause)
        fields = [
            "System.Id",
            "System.Title",
            "System.Description",
            "System.State",
            "System.WorkItemType",
            "System.Tags",
        ]
        items = _fetch_work_items_details(ids, fields)
        return [_format_work_item(it) for it in items]
    except requests.exceptions.RequestException as e:
        print(f"Error searching work items by tags {tags}: {e}")
        return []


