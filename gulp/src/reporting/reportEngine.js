import {map, groupBy} from 'lodash-compat/collection';
import {remove} from 'lodash-compat/array';
import {mapValues, assign} from 'lodash-compat/object';

// This is the business logic of the myreports client.

/**
 * Root of the client.
 *
 * Used to walk through the api needed to find a usable presentation type.
 *
 * Last call of the "walk" is buildReportConfiguration.
 */
export class ReportFinder {
  constructor(api, configBuilder) {
    this.api = api;
    this.configBuilder = configBuilder;
    this.newReportSubscribers = {};
  }

  getReportingTypes() {
    return this.api.getReportingTypes();
  }

  getReportTypes(reportingTypeId) {
    return this.api.getReportTypes(reportingTypeId);
  }

  getDataTypes(reportTypeId) {
    return this.api.getDataTypes(reportTypeId);
  }

  getPresentationTypes(reportTypeId, dataTypeId) {
    return this.api.getPresentationTypes(reportTypeId, dataTypeId);
  }

  /**
   * Get a report configuration which can be customized and later run.
   *
   * TODO: change rpId to reportTypeDataType id.
   * rpId: report presentation id
   * onNameChanged, onFilterChange, onErrorsChanged:
   *   see ReportConfiguration for definitions.
   */
  async buildReportConfiguration(rpId, onNameChanged, onFilterChange,
      onErrorsChanged) {
    const filters = await this.api.getFilters(rpId);
    const name = await this.api.getDefaultReportName(rpId);
    return await this.configBuilder.build(
      name.name, rpId, filters.filters,
      reportId => this.noteNewReport(reportId),
      onNameChanged,
      onFilterChange,
      onErrorsChanged);
  }

  /**
   * Retrieve a list of reports by this user
   * TODO: Handle searching, etc.
   */
  async getReportList() {
    return await this.api.listReports();
  }

  /**
   * Submit a callback to be called any time there is a new report created.
   *
   * returns a reference which can be used later to unsubscribe.
   */
  subscribeToReportList(callback) {
    this.newReportSubscribers[callback] = callback;
    return callback;
  }

  /**
   * Remove a callback from the new reports subscription.
   */
  unsubscribeToReportList(ref) {
    delete this.newReportSubscribers[ref];
  }

  /**
   * Let subscribers know that there is a new report.
   */
  noteNewReport(reportId) {
    for (const ref in this.newReportSubscribers) {
      if (this.newReportSubscribers.hasOwnProperty(ref)) {
        this.newReportSubscribers[ref](reportId);
      }
    }
  }
}

/**
 * Gradually build a filter for a report run with help from the api.
 *
 * Use the getHints function where available on fields to get sample
 * field values.
 *
 * Use setFilter to set simple filter values.
 *
 * Use the multifilter functions for filter values which are a collection of
 * items.
 *
 * An instance of this class stores it's own state. Use getFilter to extract
 * the complete state of the filter so far.
 *
 * Use the run function to run and store the report in the api.
 *
 * name: Initial name of the report.
 * rpId: Report Presentation id. // TODO: switch to report type data type
 * filters: List of filters supported by this report.
 * api: Reporting API instance to use.
 * onNewReport: call back when a new report has been created.
 * onNameChanged: call back when the report name changes.
 * onUpdateFilter: call back with the filter changes.
 * onErrorsChanged: call back when the list of user errors changes.
 */
export class ReportConfiguration {
  constructor(name, rpId, filters, api,
      onNewReport, onNameChanged, onUpdateFilter, onErrorsChanged) {
    this.name = name;
    this.rpId = rpId;
    this.filters = filters;
    this.simpleFilter = {};
    this.multiFilter = {};
    this.andOrFilter = {};
    this.errors = {};
    this.api = api;
    this.onNewReport = onNewReport;
    this.onNameChanged = onNameChanged;
    this.onUpdateFilter = onUpdateFilter;
    this.onErrorsChanged = onErrorsChanged;
  }

  /**
   * Return a collection of hints for a particular field and partial input.
   */
  async getHints(field, partial) {
    return await this.api.getHelp(
      this.rpId, this.getFilter(), field, partial);
  }

  callUpdateFilter() {
    const filterInfo = assign(
        {}, this.simpleFilter, this.multiFilter, this.andOrFilter);
    this.onUpdateFilter(filterInfo);
  }

  /**
   * Set a value for a single valued filter.
   */
  setFilter(field, value) {
    if (value === undefined || value === null || value === '') {
      delete this.simpleFilter[field];
    } else {
      this.simpleFilter[field] = value;
    }
    this.callUpdateFilter();
  }

  /**
   * Set a value for a multiple valued "or" filter.
   */
  addToMultifilter(field, obj) {
    if (!(field in this.multiFilter)) {
      this.multiFilter[field] = [];
    }
    if (this.multiFilter[field].findIndex(i => i.key === obj.key) === -1) {
      this.multiFilter[field].push(obj);
    }
    this.callUpdateFilter();
  }


  /**
   * Get a previously set value for a multiple valued "or" filter.
   */
  removeFromMultifilter(field, obj) {
    remove(this.multiFilter[field], i => i.key === obj.key);
    this.callUpdateFilter();
  }

  /**
   * Add a value to a "and/or" filter. i.e. tags
   */
  addToAndOrFilter(field, index, obj) {
    if (!(field in this.andOrFilter)) {
      this.andOrFilter[field] = [];
    }
    if (!(index in this.andOrFilter[field])) {
      this.andOrFilter[field][index] = [];
    }
    this.andOrFilter[field][index].push(obj);
    this.callUpdateFilter();
  }

  /**
   * Remove a value to a "and/or" filter. i.e. tags
   */
  removeFromAndOrFilter(field, index, obj) {
    const found = this.andOrFilter[field][index].findIndex(i => i.key === obj.key);
    if (found !== -1) {
      this.andOrFilter[field][index].splice(found, 1);
      if (this.andOrFilter[field][index].length < 1) {
        this.andOrFilter[field].splice(index, 1);
      }
    }
    this.callUpdateFilter();
  }

  /**
   * Build a filter suitable for sending to the run method of the api.
   */
  getFilter() {
    const filter = {...this.simpleFilter};
    for (const key in this.multiFilter) {
      if (this.multiFilter.hasOwnProperty(key)) {
        filter[key] = this.multiFilter[key].map(o => o.key);
      }
    }
    for (const key in this.andOrFilter) {
      if (this.andOrFilter.hasOwnProperty(key)) {
        filter[key] = this.andOrFilter[key].map(
          arr => arr.map(o => o.key));
      }
    }
    return filter;
  }

  /**
   * Change the name of the report.
   */
  changeReportName(name) {
    this.name = name;
    this.onNameChanged(name);
  }

  /**
   * Run callbacks to get all current stae.
   *
   * Useful at component initialization time.
   */
  runCallbacks() {
    this.onErrorsChanged(this.errors);
    this.onNameChanged(this.name);
    this.callUpdateFilter();
  }

  /**
   * Run the report.
   */
  async run() {
    try {
      const response = await this.api.runReport(
        this.rpId,
        this.name,
        this.getFilter());
      this.errors = {};
      this.onNewReport(response.id);
    } catch (exc) {
      if (exc.data) {
        const grouped = groupBy(exc.data, 'field');
        const fixed = mapValues(grouped, values => map(values, v => v.message));
        this.errors = fixed;
      }
    }
    this.onErrorsChanged(this.errors);
  }
}

/**
 * This factory just builds a ReportConfiguration.
 *
 * Having this makes unit testing easier.
 */
export class ReportConfigurationBuilder {
  constructor(api) {
    this.api = api;
  }

  async build(name, rpId, filters, onNewReport, onNameChanged, onUpdateFilter, onErrorsChanged) {
    return new ReportConfiguration(
        name, rpId, filters, this.api, onNewReport, onNameChanged, onUpdateFilter,
        onErrorsChanged);
  }
}
