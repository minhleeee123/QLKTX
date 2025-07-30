from typing import Dict, Any, List
from app.services.api_client import api_client
from app.utils.api_response import APIResponse


class ContractService:

    @staticmethod
    def get_contracts(page: int = 1, status: str = None) -> Dict[str, Any]:
        """Get list of contracts with pagination"""
        params = {'page': page, 'per_page': 20}
        if status:
            params['status'] = status

        response = api_client.get("/contracts", params)

        # API client wraps response in {success: bool, data: {...}}
        if response.get("success") and response.get("data"):
            server_data = response["data"]
            if "contracts" in server_data:
                return APIResponse.success_dict(
                    data={
                        "contracts": server_data["contracts"],
                        "pagination": server_data.get("pagination", {}),
                    }
                )
            else:
                return response["data"]  # Return whatever the server sent
        else:
            return APIResponse.error_dict(
                message=response.get("message", "Không thể lấy danh sách hợp đồng")
            )

    @staticmethod
    def get_contract(contract_id: int) -> Dict[str, Any]:
        """Get contract details by ID"""
        response = api_client.get(f"/contracts/{contract_id}")

        # API client wraps response in {success: bool, data: {...}}
        if response.get("success") and response.get("data"):
            server_data = response["data"]
            if "contract" in server_data:
                return APIResponse.success_dict(
                    data={"contract": server_data["contract"]}
                )
            else:
                return response["data"]  # Return whatever the server sent
        else:
            return APIResponse.error_dict(
                message=response.get("message", "Không thể lấy thông tin hợp đồng")
            )

    @staticmethod
    def update_contract(contract_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update contract information"""
        response = api_client.put(f"/contracts/{contract_id}", data)

        # API client wraps response in {success: bool, data: {...}}
        if response.get("success") and response.get("data"):
            server_data = response["data"]
            return {
                "success": True,
                "message": server_data.get("message", "Cập nhật hợp đồng thành công"),
                "contract": server_data.get("contract"),
            }
        else:
            return {
                "success": False,
                "error": response.get("error", "Lỗi không xác định"),
            }

    @staticmethod
    def get_contract_statistics() -> Dict[str, Any]:
        """Get contract statistics"""
        response = api_client.get("/contracts/statistics")

        # API client wraps response in {success: bool, data: {...}}
        if response.get("success") and response.get("data"):
            server_data = response["data"]
            if "statistics" in server_data:
                return APIResponse.success_dict(
                    data={"statistics": server_data["statistics"]}
                )
            else:
                return response["data"]  # Return whatever the server sent
        else:
            return APIResponse.error_dict(
                message=response.get("message", "Không thể lấy thống kê hợp đồng")
            )
