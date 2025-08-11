from typing import Any, Dict, List

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
    def renew_contract(contract_id: int, renewal_months: int) -> Dict[str, Any]:
        """Renew contract for specified months"""
        data = {'renewal_months': renewal_months}
        response = api_client.post(f"/contracts/{contract_id}/renew", data)

        if response.get("success") and response.get("data"):
            server_data = response["data"]
            return {
                "success": True,
                "message": response.get("message", "Gia hạn hợp đồng thành công"),
                "contract": server_data.get("contract"),
            }
        else:
            return {
                "success": False,
                "error": response.get("message", "Lỗi không xác định"),
            }

    @staticmethod
    def terminate_contract(contract_id: int, reason: str) -> Dict[str, Any]:
        """Terminate contract early"""
        data = {'reason': reason}
        response = api_client.post(f"/contracts/{contract_id}/terminate", data)

        if response.get("success") and response.get("data"):
            server_data = response["data"]
            return {
                "success": True,
                "message": response.get("message", "Chấm dứt hợp đồng thành công"),
                "contract": server_data.get("contract"),
            }
        else:
            return {
                "success": False,
                "error": response.get("message", "Lỗi không xác định"),
            }

    @staticmethod
    def get_expiring_contracts(days: int = 30) -> Dict[str, Any]:
        """Get contracts expiring soon"""
        params = {'days': days}
        response = api_client.get("/contracts/expiring-soon", params)

        if response.get("success") and response.get("data"):
            server_data = response["data"]
            return APIResponse.success_dict(
                data={
                    "contracts": server_data.get("contracts", []),
                    "total_count": server_data.get("total_count", 0),
                    "days_threshold": server_data.get("days_threshold", days),
                }
            )
        else:
            return APIResponse.error_dict(
                message=response.get("message", "Không thể lấy danh sách hợp đồng sắp hết hạn")
            )

    @staticmethod
    def export_contracts() -> str:
        """Export contracts to Excel"""
        return "/contracts/export"  # Return URL for download

    @staticmethod
    def get_contract_history(contract_id: int, page: int = 1) -> Dict[str, Any]:
        """Get contract history"""
        params = {'page': page, 'per_page': 20}
        response = api_client.get(f"/contracts/{contract_id}/history", params)

        if response.get("success") and response.get("data"):
            return APIResponse.success_dict(data=response["data"])
        else:
            return APIResponse.error_dict(
                message=response.get("message", "Không thể lấy lịch sử hợp đồng")
            )

    @staticmethod
    def export_contract_history(contract_id: int) -> str:
        """Export contract history to Excel"""
        return f"/contracts/{contract_id}/export-history"  # Return URL for download

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