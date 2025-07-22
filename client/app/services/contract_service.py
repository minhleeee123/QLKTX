from typing import Dict, Any, List
from app.services.api_client import api_client


class ContractService:
    
    @staticmethod
    def get_contracts(page: int = 1, status: str = None) -> Dict[str, Any]:
        """Get list of contracts with pagination"""
        params = {'page': page, 'per_page': 20}
        if status:
            params['status'] = status
            
        response = api_client.get("/contracts", params)
        
        # Handle server response format
        if response and 'contracts' in response:
            return {
                'success': True,
                'contracts': response['contracts'],
                'pagination': response.get('pagination', {})
            }
        elif response and response.get('success'):
            return response
        else:
            return {
                'success': False,
                'error': response.get('error', 'Không thể lấy danh sách hợp đồng')
            }
    
    @staticmethod
    def get_contract(contract_id: int) -> Dict[str, Any]:
        """Get contract details by ID"""
        response = api_client.get(f"/contracts/{contract_id}")
        
        # Handle server response format
        if response and 'contract' in response:
            return {
                'success': True,
                'contract': response['contract']
            }
        elif response and response.get('success'):
            return response
        else:
            return {
                'success': False,
                'error': response.get('error', 'Không thể lấy thông tin hợp đồng')
            }
    
    @staticmethod
    def update_contract(contract_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update contract information"""
        response = api_client.put(f"/contracts/{contract_id}", data)
        
        if response and (response.get('success') or 'message' in response):
            return {
                'success': True,
                'message': response.get('message', 'Cập nhật hợp đồng thành công'),
                'contract': response.get('contract')
            }
        else:
            return {
                'success': False,
                'error': response.get('error', response if isinstance(response, str) else 'Lỗi không xác định')
            }
    
    @staticmethod
    def get_contract_statistics() -> Dict[str, Any]:
        """Get contract statistics"""
        response = api_client.get("/contracts/statistics")
        
        if response and 'statistics' in response:
            return {
                'success': True,
                'statistics': response['statistics']
            }
        elif response and response.get('success'):
            return response
        else:
            return {
                'success': False,
                'error': response.get('error', 'Không thể lấy thống kê hợp đồng')
            }
