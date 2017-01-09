// Abstract the details of building urls and serializing requests for the
// reporting api.
//
// This uses the fetch api. Fetch works somewhat differently from jQuery.ajax.
// This module encapsulates all of that. Errors are translated to JS exceptions.


class Api {
  constructor(myJobsApi) {
    this.myJobsApi = myJobsApi;
  }

  async getFromReportingApi(url) {
    return this.myJobsApi.get(url);
  }

  async postToReportingApi(url, data) {
    return this.myJobsApi.post(url, data);
  }

  async listReports() {
    const response = await this.getFromReportingApi(
      '/reports/api/list_reports');
    return response.reports;
  }

  async getReportInfo(reportId) {
    const response = await this.getFromReportingApi(
      '/reports/api/report_info?report_id=' + reportId);
    return response.report_details;
  }

  async getSetUpMenuChoices(reportingType, reportType, dataType) {
    const formData = {
      reporting_type: reportingType,
      report_type: reportType,
      data_type: dataType,
    };
    return this.postToReportingApi(
      '/reports/api/select_data_type_api', formData);
  }

  async getExportOptions(reportId) {
    return await this.getFromReportingApi(
      '/reports/api/export_options_api?report_id=' + reportId);
  }

  async getDefaultReportName(reportDataId) {
    const formData = {
      report_data_id: reportDataId,
    };
    return await this.postToReportingApi(
          '/reports/api/default_report_name',
          formData);
  }

  async getFilters(reportDataId) {
    const formData = {
      report_data_id: reportDataId,
    };
    const promise = this.postToReportingApi(
          '/reports/api/filters',
          formData);
    return (await promise);
  }

  async getHelp(reportDataId, filter, field, partial) {
    const formData = {
      report_data_id: reportDataId,
      filter: JSON.stringify(filter),
      field: field,
      partial: partial,
    };
    const promise = this.postToReportingApi(
          '/reports/api/help',
          formData);
    return (await promise);
  }

  async runReport(reportDataId, name, filter) {
    const formData = {
      name: name,
      filter: JSON.stringify(filter),
      report_data_id: reportDataId,
    };
    return await this.postToReportingApi(
      '/reports/api/run_report',
      formData);
  }

  async runTrialReport(reportDataId, filter, values) {
    const formData = {
      filter: JSON.stringify(filter),
      values: JSON.stringify(values),
      report_data_id: reportDataId,
    };
    return await this.postToReportingApi(
      '/reports/api/run_trial_report',
      formData);
  }

  async refreshReport(reportId) {
    const formData = {
      report_id: reportId,
    };
    return await this.postToReportingApi(
      '/reports/api/refresh_report',
      formData);
  }
}

export {Api as default};
