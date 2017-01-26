// Abstract the details of building urls and serializing requests for the
// analytics api.
//
// This uses the fetch api. Fetch works somewhat differently from jQuery.ajax.
// This module encapsulates all of that. Errors are translated to JS exceptions.


export default class Api {
  constructor(api) {
    this.api = api;
  }
  // Get initial loading data for when app starts
  async getInitialPageData(start, end) {
    const loadStartingPointReport = await this.api.get('/analytics/api/available-reports');
    const initialPageRequest = {
      'date_start': start + ' 00:00:00',
      'date_end': end,
      'active_filters': [],
      'report': loadStartingPointReport.reports[0].value,
    };
    return await this.api.post('/analytics/api/dynamic', {'request': JSON.stringify(initialPageRequest)});
  }
  // Get the primary dimensions for when the app loads
  async getPrimaryDimensions() {
    return await this.api.get('/analytics/api/available-reports');
  }
  // Get the initial report for displaying the right data when page loads
  async getStartingPointReport() {
    const setStartingPointReport = await this.api.get('/analytics/api/available-reports');
    return setStartingPointReport.reports[0].value;
  }
  // Get the data requested from filtering on the table
  async getSelectedFilterData(storedFilters, currentReport, date) {
    const selectedFilterRequest = {
      'date_start': date.startDate,
      'date_end': date.endDate,
      'active_filters': storedFilters,
      'report': currentReport,
    };
    return await this.api.post('/analytics/api/dynamic', {'request': JSON.stringify(selectedFilterRequest)});
  }
  // Get the data from the main dimensions selected from sidebar
  async getMainDimensionData(mainDimension, start, end) {
    const mainDimensionDataRequest = {
      'date_start': start,
      'date_end': end,
      'active_filters': [],
      'report': mainDimension,
    };
    return await this.api.post('/analytics/api/dynamic', {'request': JSON.stringify(mainDimensionDataRequest)});
  }
  // Get the date range data selected from the Quick Range Selections
  async getDateRangeData(start, end, mainDimension, activeFilters) {
    const setDateRangeDataRequest = {
      'date_start': start,
      'date_end': end,
      'active_filters': activeFilters,
      'report': mainDimension,
    };
    return await this.api.post('/analytics/api/dynamic', {'request': JSON.stringify(setDateRangeDataRequest)});
  }
  // Get the custom date range selected from the Range Calendars
  async customDateRangeData(start, end, mainDimension, activeFilters) {
    const setCustomDateRangeDataRequest = {
      'date_start': start + ' 00:00:00',
      'date_end': end + ' 23:59:59',
      'active_filters': activeFilters,
      'report': mainDimension,
    };
    return await this.api.post('/analytics/api/dynamic', {'request': JSON.stringify(setCustomDateRangeDataRequest)});
  }
}
