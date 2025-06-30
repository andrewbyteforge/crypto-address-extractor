import requests

class IAPIService:
    def __init__(self, api_key):
        self.api_key = api_key
        self.server = "iapi.chainalysis.com"

    def _get(self, path, params=None):
        header = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Token": self.api_key
        }
        url = f"https://{self.server}{path}"
        req = requests.get(url, headers=header, params=params)
        if req.status_code != 200:
            raise Exception(req.status_code, req.text)
        json_data = req.json()
        return json_data

    # --------------------------------
    # Cluster Info Endpoints
    # https://reactor.chainalysis.com/docs/investigations/#tag/Cluster-info
    # --------------------------------

    def get_cluster_name_and_category(self, address, asset):
        """
        Cluster Name and Category
        For a given cryptocurrency address, this endpoint returns
        the respective cluster’s name, category, and cluster root address.
        https://reactor.chainalysis.com/docs/investigations/#operation/getMatchingAddresses
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
        :param: params - dict value of query parameters: page, limit

        https://reactor.chainalysis.com/docs/investigations/#operation/getAddressesForCluster
        """
        path = f"/clusters/{address}/{asset}/addresses"
        return self._get(path, params)

    def get_cluster_balance(self, address, asset, output_asset="NATIVE"):
        """
        Cluster balance
        This endpoint returns cluster balance details including
        address count, transfer count, deposit count, withdrawal count,
        and total sent and received fees for a given cryptocurrency address.
        https://reactor.chainalysis.com/docs/investigations/#operation/getAddressSummary
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
        :param: params - dict value of query parameters: page, limit
        https://reactor.chainalysis.com/docs/investigations/#operation/getTransactionsForCluster
        """
        path = f"/clusters/{address}/{asset}/transactions"
        return self._get(path, params)

    def get_cluster_counterparties(self, address, asset, output_asset="NATIVE", params=None):
        """
        Cluster Counterparties
        This endpoint returns the counterparties associated with
        a specific cluster for a given cryptocurrency address and asset.
        :params: output_asset: NATIVE or USD
        """
        assert (output_asset in ["NATIVE", "USD"]), "output_asset must be 'NATIVE' or 'USD'"
        params = {
            "outputAsset": output_asset
        }
        path = f"/clusters/{address}/{asset}/counterparties"
        return self._get(path, params)

    # --------------------------------
    # Transaction Info Endpoints
    # https://reactor.chainalysis.com/docs/investigations/#tag/Transaction-info
    # --------------------------------

    def get_transaction_time_and_asset(self, hash, params=None):
        """
        Transaction Time & Asset
        This endpoint returns the asset, blockhash, block height
        and block time for a given transaction hash.
        :param: params - dict value of query parameters: filterAsset
        https://reactor.chainalysis.com/docs/investigations/#operation/getMatchingTransactions
        """
        path = f"/transactions/{hash}"
        return self._get(path, params)

    def get_transaction_details(self, hash, asset):
        """
        Transaction Time & Asset
        This endpoint returns the asset, blockhash, block height
        and block time for a given transaction hash.
        https://reactor.chainalysis.com/docs/investigations/#operation/getTransactionDetails
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
    # https://reactor.chainalysis.com/docs/investigations/#tag/Exposure-info
    # --------------------------------

    def get_exposure_by_category(self, address, asset, direction, output_asset="NATIVE"):
        """
        Exposure
        This endpoint returns direct and indirect exposure values and percentages by category for a given cluster.
        :params: output_asset: NATIVE or USD
        https://reactor.chainalysis.com/docs/investigations/#operation/getDirectedExposureByCategory
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
        :params: output_asset: NATIVE or USD
        https://reactor.chainalysis.com/docs/investigations/#operation/getDirectedExposureByService
        """
        assert (output_asset in ["NATIVE", "USD"]), "output_asset must be 'NATIVE' or 'USD'"
        params = {
            "outputAsset": output_asset
        }
        path = f"/exposures/clusters/{address}/{asset}/directions/{direction}/services"
        return self._get(path, params=params)

    # --------------------------------
    # Wallet Observations Endpoints
    # https://reactor.chainalysis.com/docs/investigations/#tag/Wallet-observations
    # --------------------------------

    def get_cluster_observations_by_ip(self, ip, params=None):
        """
        Get Observations by Cluster endpoint
        https://reactor.chainalysis.com/docs/investigations/#operation/getObservationsForIp
        :param: params - dict value of query parameters: startTime, endTime, page
        """
        path = f"/observations/ips/{ip}"
        return self._get(path, params)

    def get_observations_by_country(self, country, params=None):
        """
        Get Observations by Country endpoint
        https://reactor.chainalysis.com/docs/investigations/#operation/getObservationsForCountry
        :param: params - dict value of query parameters: startTime, endTime, page

        """
        path = f"/observations/countries/{country}"
        return self._get(path, params)

    def get_observations_by_city(self, country, city, params=None):
        """
        Get Observations by City endpoint
        https://reactor.chainalysis.com/docs/investigations/#operation/getObservationsForLocation
        :param: params - dict value of query parameters: startTime, endTime, page

        """
        path = f"/observations/countries/{country}/cities/{city}"
        return self._get(path, params)

    def get_observations_for_cluster(self, address, params=None):
        """
        Get Observations by Cluster endpoint
        https://reactor.chainalysis.com/docs/investigations/#operation/getObservationsForCluster
        :param: params - dict value of query parameters: startTime, endTime, page
        """
        path = f"/observations/clusters/{address}/BTC"
        return self._get(path, params)

    # --------------------------------
    # Usage Info Endpoints
    # https://reactor.chainalysis.com/docs/investigations/#tag/Usage-info
    # --------------------------------

    def get_usage_by_org(self, startDate, endDate, params=None):
        """
        Get Usage by Organization endpoint
        https://reactor.chainalysis.com/docs/investigations/#operation/getUsageOrg
        :param: params - dict value of query parameters: grouping
        """
        path = f"/usage/org/{startDate}/{endDate}"
        return self._get(path, params)

    def get_usage_by_user(self, startDate, endDate, params=None):
        """
        Get Usage by User endpoint
        https://reactor.chainalysis.com/docs/investigations/#operation/getUsageUser
        :param: params - dict value of query parameters: grouping
        """
        path = f"/usage/user/{startDate}/{endDate}"
        return self._get(path, params)

Using query parameters

The Investigations API accepts query parameters and cursor based pagination for certain requests. It’s recommended to use query parameters to only return the data you need.

Which query parameters are available?

Check the endpoint for available query parameters.