import requests
import time
import logging

class IAPIService:
    def __init__(self, api_key):
        self.api_key = api_key
        self.server = "iapi.chainalysis.com"
        self.max_retries = 3
        self.retry_delay = 1  # seconds
        self.logger = logging.getLogger(__name__)
        
        # Use session for connection pooling - this is the key performance improvement
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Token": self.api_key
        })
        
        # Configure connection pooling
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=100,  # Number of connection pools to cache
            pool_maxsize=100,      # Maximum number of connections to save in the pool
            max_retries=0          # We handle retries manually
        )
        self.session.mount('https://', adapter)
        self.session.mount('http://', adapter)

    def _get(self, path, params=None):
        url = f"https://{self.server}{path}"
        
        for attempt in range(self.max_retries):
            try:
                # Use session instead of requests.get for connection reuse
                req = self.session.get(url, params=params, timeout=30)
                
                if req.status_code == 200:
                    return req.json()
                elif req.status_code == 503:
                    # Service unavailable, retry with exponential backoff
                    if attempt < self.max_retries - 1:
                        wait_time = self.retry_delay * (2 ** attempt)
                        time.sleep(wait_time)
                        continue
                    else:
                        raise Exception(req.status_code, req.text)
                else:
                    raise Exception(req.status_code, req.text)
                    
            except requests.exceptions.Timeout:
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                else:
                    raise Exception("Request timeout", "The API request timed out")
                    
            except requests.exceptions.ConnectionError:
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                else:
                    raise Exception("Connection error", "Failed to connect to API")
        
        raise Exception(503, "Service unavailable after retries")
    
    def close(self):
        """Close the session to free up resources."""
        self.session.close()

    # --------------------------------
    # Cluster Info Endpoints
    # --------------------------------

    def get_cluster_name_and_category(self, address, asset):
        """
        Cluster Name and Category
        For a given cryptocurrency address, this endpoint returns
        the respective cluster's name, category, and cluster root address.
        """
        params = {
            "filterAsset": asset
        }
        path = f"/clusters/{address}"
        return self._get(path, params)

    def get_cluster_addresses(self, address, asset, params=None):
        """
        Cluster Addresses
        This endpoint returns a list of addresses associated
        with a specific cluster for given a cryptocurrency address and asset.
        """
        path = f"/clusters/{address}/{asset}/addresses"
        return self._get(path, params)

    def get_cluster_balance(self, address, asset, output_asset="NATIVE"):
        """
        Cluster balance
        This endpoint returns cluster balance details including
        address count, transfer count, deposit count, withdrawal count,
        and total sent and received fees for a given cryptocurrency address.
        """
        assert (output_asset in ["NATIVE", "USD"]), "output_asset must be 'NATIVE' or 'USD'"
        params = {
            "outputAsset": output_asset
        }
        path = f"/clusters/{address}/{asset}/summary"
        return self._get(path, params=params)

    def get_cluster_transactions(self, address, asset, params=None):
        """
        Cluster Transactions
        This endpoint returns the transaction hashes associated
        with a specific cluster for a given cryptocurrency address and asset.
        """
        path = f"/clusters/{address}/{asset}/transactions"
        return self._get(path, params)

    def get_cluster_counterparties(self, address, asset, output_asset="NATIVE", params=None):
        """
        Cluster Counterparties
        This endpoint returns the counterparties associated with
        a specific cluster for a given cryptocurrency address and asset.
        """
        assert (output_asset in ["NATIVE", "USD"]), "output_asset must be 'NATIVE' or 'USD'"
        if params is None:
            params = {}
        params["outputAsset"] = output_asset
        path = f"/clusters/{address}/{asset}/counterparties"
        return self._get(path, params)

    # --------------------------------
    # Transaction Info Endpoints
    # --------------------------------

    def get_transaction_time_and_asset(self, hash, params=None):
        """
        Transaction Time & Asset
        This endpoint returns the asset, blockhash, block height
        and block time for a given transaction hash.
        """
        path = f"/transactions/{hash}"
        return self._get(path, params)

    def get_transaction_details(self, hash, asset):
        """
        Transaction Time & Asset
        This endpoint returns the asset, blockhash, block height
        and block time for a given transaction hash.
        """
        path = f"/transactions/{hash}/{asset}/details"
        return self._get(path)

    def get_address_transactions(self, address, asset, direction):
        """
        Transaction hashes by address
        This endpoint returns transaction hashes of transactions
        where the given address is either a sender or receiver.
        """
        params = {
            "direction": direction
        }
        path = f"/addresses/{address}/{asset}/transactions"
        return self._get(path, params=params)

    # --------------------------------
    # Exposure Info Endpoint
    # --------------------------------

    def get_exposure_by_category(self, address, asset, direction, output_asset="NATIVE"):
        """
        Exposure
        This endpoint returns direct and indirect exposure values and percentages by category for a given cluster.
        """
        assert (output_asset in ["NATIVE", "USD"]), "output_asset must be 'NATIVE' or 'USD'"
        params = {
            "outputAsset": output_asset
        }
        path = f"/exposures/clusters/{address}/{asset}/directions/{direction}"
        return self._get(path, params=params)

    def get_exposure_by_service(self, address, asset, direction, output_asset="NATIVE"):
        """
        Exposure
        This endpoint returns direct and indirect exposure values and percentages by services for a given cluster.
        """
        assert (output_asset in ["NATIVE", "USD"]), "output_asset must be 'NATIVE' or 'USD'"
        params = {
            "outputAsset": output_asset
        }
        path = f"/exposures/clusters/{address}/{asset}/directions/{direction}/services"
        return self._get(path, params=params)

    # --------------------------------
    # Wallet Observations Endpoints
    # --------------------------------

    def get_cluster_observations_by_ip(self, ip, params=None):
        """
        Get Observations by Cluster endpoint
        """
        path = f"/observations/ips/{ip}"
        return self._get(path, params)

    def get_observations_by_country(self, country, params=None):
        """
        Get Observations by Country endpoint
        """
        path = f"/observations/countries/{country}"
        return self._get(path, params)

    def get_observations_by_city(self, country, city, params=None):
        """
        Get Observations by City endpoint
        """
        path = f"/observations/countries/{country}/cities/{city}"
        return self._get(path, params)

    def get_observations_for_cluster(self, address, params=None):
        """
        Get Observations by Cluster endpoint
        """
        path = f"/observations/clusters/{address}/BTC"
        return self._get(path, params)

    # --------------------------------
    # Usage Info Endpoints
    # --------------------------------

    def get_usage_by_org(self, startDate, endDate, params=None):
        """
        Get Usage by Organization endpoint
        """
        path = f"/usage/org/{startDate}/{endDate}"
        return self._get(path, params)

    def get_usage_by_user(self, startDate, endDate, params=None):
        """
        Get Usage by User endpoint
        """
        path = f"/usage/user/{startDate}/{endDate}"
        return self._get(path, params)
