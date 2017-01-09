import React, {PropTypes, Component} from 'react';
import HelpText from '../../common/ui/HelpText';
import {connect} from 'react-redux';
import warning from 'warning';
import {scrollUp} from 'common/dom';
import {forEach, map} from 'lodash-compat/collection';
import {keys} from 'lodash-compat/object';
import {typingDebounce} from 'common/debounce';
import {blendControls} from './util';
import {
  setSimpleFilterAction,
  addToOrFilterAction,
  removeFromOrFilterAction,
  addToAndOrFilterAction,
  removeFromAndOrFilterAction,
  deleteFilterAction,
  emptyFilterAction,
  setReportNameAction,
  unlinkFilterAction,
} from '../actions/report-state-actions';

import {
  doGetHelp,
  doUpdateFilterWithDependencies,
  doRunReport,
} from '../actions/compound-actions';

import FilterDateRange from './FilterDateRange';
import FilterSearchDropdown from './FilterSearchDropdown';
import FilterCityState from './FilterCityState';
import FieldWrapper from 'common/ui/FieldWrapper';
import DataTypeSelectBar from './DataTypeSelectBar';
import TextField from 'common/ui/TextField';
import SelectControls from 'common/ui/SelectControls';
import TagSelect from 'common/ui/tags/TagSelect';
import TagAnd from 'common/ui/tags/TagAnd';

class SetUpReport extends Component {
  onIntentionChange(intention, selectedObject) {
    const {history, category, dataSet} = this.props;
    if (selectedObject && selectedObject.link) {
      const link = selectedObject.link;
      if (link === 'analytics') {
        window.location = '/analytics/view/main';
        return;
      }
    }
    history.pushState(null, '/', {intention, category, dataSet});
  }

  onCategoryChange(category) {
    const {history, intention, dataSet} = this.props;
    history.pushState(null, '/', {intention, category, dataSet});
  }

  onDataSetChange(dataSet) {
    const {history, intention, category} = this.props;
    history.pushState(null, '/', {intention, category, dataSet});
  }

  getHints(field, value) {
    const {dispatch, reportDataId, currentFilter} = this.props;
    return dispatch(doGetHelp(reportDataId, currentFilter, field, value));
  }

  async handleRunReport(e) {
    e.preventDefault();

    const {dispatch, reportName, currentFilter, reportDataId} = this.props;

    scrollUp();
    await dispatch(doRunReport(reportDataId, reportName, currentFilter));
    const {reportNameErrors} = this.props;
    if (!reportNameErrors) {
      this.props.history.pushState(null, '/');
    }
  }

  dispatchFilterAction(action) {
    const {dispatch} = this.props;
    dispatch(action);
    this.dispatchUpdateFilterWithDependencies();
  }

  dispatchUpdateFilterWithDependencies() {
    const {dispatch, filterInterface, reportDataId} = this.props;
    return dispatch(
      doUpdateFilterWithDependencies(filterInterface, reportDataId));
  }

  renderTagsControl(col) {
    const {
      dispatch,
      currentFilter,
      hints,
      fieldsLoading,
    } = this.props;


    let selectValue;
    if (currentFilter[col.filter]) {
      if (currentFilter[col.filter].nolink) {
        selectValue = 'untagged';
      } else {
        selectValue = 'tags';
      }
    } else {
      selectValue = 'none';
    }
    const switchControl = (value) => {
      if (value === 'tags') {
        dispatch(deleteFilterAction(col.filter));
        dispatch(emptyFilterAction(col.filter));
        this.dispatchUpdateFilterWithDependencies();
      } else if (value === 'untagged') {
        dispatch(deleteFilterAction(col.filter));
        dispatch(unlinkFilterAction(col.filter));
        this.dispatchUpdateFilterWithDependencies();
      } else {
        dispatch(deleteFilterAction(col.filter));
        this.dispatchUpdateFilterWithDependencies();
      }
    };
    const choices = [
      {value: 'none', display: 'No filter', render: () => ''},
      {
        value: 'tags',
        display: 'Filter by tags',
        render: () => (
          <TagAnd
            available={hints[col.filter] || []}
            selected={currentFilter[col.filter]}
            onChoose={(i, t) =>
              this.dispatchFilterAction(
                addToAndOrFilterAction(col.filter, i, t))}
            onRemove={(i, t) =>
              this.dispatchFilterAction(
                removeFromAndOrFilterAction(col.filter, i, t))}
          />
        ),
      },
      {
        value: 'untagged',
        display: 'Filter only untagged items',
        render: () => '',
      },
    ];

    return (
      <FieldWrapper
        key={col.filter}
        label={col.display}>

        <SelectControls
          choices={choices}
          value={selectValue}
          loading={fieldsLoading[col.filter]}
          onSelect={v => switchControl(v)}/>

      </FieldWrapper>
    );
  }

  renderMultiselectControl(col) {
    const {
      dispatch,
      currentFilter,
      hints,
      fieldsLoading,
    } = this.props;

    const selectValue = currentFilter[col.filter] ? 'items' : 'none';
    const switchControl = (value) => {
      if (value === 'items') {
        dispatch(deleteFilterAction(col.filter));
        dispatch(emptyFilterAction(col.filter));
        this.dispatchUpdateFilterWithDependencies();
      } else {
        dispatch(deleteFilterAction(col.filter));
        this.dispatchUpdateFilterWithDependencies();
      }
    };
    const choices = [
      {value: 'none', display: 'No filter', render: () => ''},
      {
        value: 'items',
        display: 'Filter by ' + col.display,
        render: () => (
          <TagSelect
            selected={currentFilter[col.filter]}
            available={hints[col.filter] || []}
            onChoose={vs =>
              this.dispatchFilterAction(
                addToOrFilterAction(col.filter, vs))}
            onRemove={vs =>
              this.dispatchFilterAction(
                removeFromOrFilterAction(col.filter, vs))}
            searchPlaceholder="Filter these choices"
            placeholder="Make a selection"
          />
        ),
      },
    ];

    return (
      <FieldWrapper
        key={col.filter}
        label={col.display}>

        <SelectControls
          choices={choices}
          value={selectValue}
          loading={fieldsLoading[col.filter]}
          onSelect={v => switchControl(v)}/>

      </FieldWrapper>
    );
  }

  renderCompositeMultiselectWithTagsControl(col) {
    const {
      dispatch,
      currentFilter,
      hints,
      fieldsLoading,
    } = this.props;

    const namesCol = col.interfaces.search_multiselect;
    const tagsCol = col.interfaces.tags;
    let selectValue;
    if (currentFilter[namesCol.filter]) {
      selectValue = 'names';
    } else if (currentFilter[tagsCol.filter]) {
      if (currentFilter[tagsCol.filter].nolink) {
        selectValue = 'untagged';
      } else {
        selectValue = 'tags';
      }
    } else {
      selectValue = 'none';
    }
    const switchControl = (value) => {
      if (value === 'names') {
        dispatch(deleteFilterAction(namesCol.filter));
        dispatch(deleteFilterAction(tagsCol.filter));
        dispatch(emptyFilterAction(namesCol.filter));
        this.dispatchUpdateFilterWithDependencies();
      } else if (value === 'tags') {
        dispatch(deleteFilterAction(namesCol.filter));
        dispatch(deleteFilterAction(tagsCol.filter));
        dispatch(emptyFilterAction(tagsCol.filter));
        this.dispatchUpdateFilterWithDependencies();
      } else if (value === 'untagged') {
        dispatch(deleteFilterAction(namesCol.filter));
        dispatch(deleteFilterAction(tagsCol.filter));
        dispatch(unlinkFilterAction(tagsCol.filter));
        this.dispatchUpdateFilterWithDependencies();
      } else {
        dispatch(deleteFilterAction(namesCol.filter));
        dispatch(deleteFilterAction(tagsCol.filter));
        this.dispatchUpdateFilterWithDependencies();
      }
    };
    const choices = [
      {value: 'none', display: 'No filter', render: () => ''},
      {
        value: 'names',
        display: 'Filter by name',
        render: () => (
          <TagSelect
            selected={currentFilter[namesCol.filter]}
            available={hints[namesCol.filter] || []}
            onChoose={vs =>
              this.dispatchFilterAction(
                addToOrFilterAction(namesCol.filter, vs))}
            onRemove={vs =>
              this.dispatchFilterAction(
                removeFromOrFilterAction(namesCol.filter, vs))}
            searchPlaceholder="Filter these choices"
            placeholder="Make a selection"
          />
        ),
      },
      {
        value: 'tags',
        display: 'Filter by tags',
        render: () => (
          <TagAnd
            available={hints[tagsCol.filter] || []}
            selected={currentFilter[tagsCol.filter]}
            onChoose={(i, t) =>
              this.dispatchFilterAction(
                addToAndOrFilterAction(tagsCol.filter, i, t))}
            onRemove={(i, t) =>
              this.dispatchFilterAction(
                removeFromAndOrFilterAction(tagsCol.filter, i, t))}
          />
        ),
      },
      {
        value: 'untagged',
        display: 'Filter only untagged items',
        render: () => '',
      },
    ];
    const counter = '(' +
      (hints[namesCol.filter] || []).length +
      ' ' + col.display.toLowerCase() + ' available)';
    const loading = (
      fieldsLoading[tagsCol.filter] || fieldsLoading[namesCol.filter]);

    return (
      <FieldWrapper
        key={col.filter}
        label={col.display}>

        <SelectControls
          choices={choices}
          value={selectValue}
          loading={loading}
          decoration={counter}
          onSelect={v => switchControl(v)}/>

      </FieldWrapper>
    );
  }

  renderCompositeControl(col) {
    const {interfaces} = col;
    if (interfaces && interfaces.search_multiselect && interfaces.tags) {
      return this.renderCompositeMultiselectWithTagsControl(col);
    }
    warning(false,
      'Unknown composite interface types: ' + keys(interfaces).join(','));
  }

  render() {
    const {
      dispatch,
      currentFilter,
      filterInterface,
      reportName,
      reportNameErrors,
      hints,
      fieldsLoading,
      isValid,
      recordCount,
    } = this.props;

    const rows = [];
    if (filterInterface.length) {
      const errorTexts = map(reportNameErrors, e => e.message);
      rows.push(
        <FieldWrapper
          key="reportName"
          label="Report Name"
          helpText="Name will appear in downloaded filenames."
          errors={errorTexts}>
          <TextField
            value={reportName}
            name=""
            autoFocus="autofocus"
            onChange={v => dispatch(setReportNameAction(v.target.value))}/>
        </FieldWrapper>
      );
      forEach(blendControls(filterInterface), col => {
        switch (col.interface_type) {
        case 'date_range':
          const begin = (currentFilter[col.filter] || [])[0];
          const end = (currentFilter[col.filter] || [])[1];

          rows.push(
            <FieldWrapper key={col.filter} label="Date range">
              <FilterDateRange
                id={col.filter}
                updateFilter={v =>
                  this.dispatchFilterAction(
                    setSimpleFilterAction(col.filter, v))}
                begin={begin}
                end={end}
                />
            </FieldWrapper>
          );
          break;
        case 'search_select':
          rows.push(
            <FieldWrapper key={col.filter} label={col.display}>
              <FilterSearchDropdown
                id={col.filter}
                value={currentFilter[col.filter] || ''}
                updateFilter={v =>
                  this.dispatchFilterAction(
                    setSimpleFilterAction(col.filter, v))}
                getHints={typingDebounce(v => this.getHints(col.filter, v))}
                loading={fieldsLoading[col.filter]}
                hints={hints[col.filter]}/>
            </FieldWrapper>
          );
          break;
        case 'city_state':
          const values = currentFilter[col.filter] || {};
          rows.push(
            <FieldWrapper key={col.filter} label={col.display}>
              <FilterCityState
                id={col.filter}
                values={values}
                updateFilter={v =>
                  this.dispatchFilterAction(
                    setSimpleFilterAction(col.filter, v))}
                getHints={typingDebounce((f, v) => this.getHints(f, v))}
                cityLoading={fieldsLoading.city}
                stateLoading={fieldsLoading.state}
                hints={hints}/>
            </FieldWrapper>
          );
          break;
        case 'tags':
          rows.push(this.renderTagsControl(col));
          break;
        case 'search_multiselect':
          rows.push(this.renderMultiselectControl(col));
          break;
        case 'composite':
          rows.push(this.renderCompositeControl(col));
          break;
        default:
          warning(false, 'Unknown interface type: ' + col.interface_type);
        }
      });
    }

    return (
      <div>
        <DataTypeSelectBar
          onIntentionChange={(v, o) => this.onIntentionChange(v, o)}

          onCategoryChange={v => this.onCategoryChange(v)}

          onDataSetChange={v => this.onDataSetChange(v)}
          />
        {rows}
        <div className="row actions text-center">
          <div className="col-xs-12 col-md-4"></div>
          <div className="col-xs-12 col-md-8">
            {!isValid ?
              <HelpText
                message="Current set of filters would result in an empty report"
              /> :
              <p>
                ({recordCount} records will be included in this report)
              </p>}
            <button
              disabled={!isValid}
              className={'button' + (isValid ? ' primary' : '')}
              onClick={ e => this.handleRunReport(e)}>
              Run Report
            </button>
          </div>
        </div>
      </div>
    );
  }
}

SetUpReport.propTypes = {
  dispatch: PropTypes.func.isRequired,
  history: PropTypes.object.isRequired,
  reportName: PropTypes.string,
  reportNameErrors: PropTypes.arrayOf(PropTypes.string.isRequired),
  intention: PropTypes.string,
  category: PropTypes.string,
  dataSet: PropTypes.string,
  reportDataId: PropTypes.number,
  hints: PropTypes.object.isRequired,
  isValid: PropTypes.bool.isRequired,
  recordCount: PropTypes.number.isRequired,
  currentFilter: PropTypes.object.isRequired,
  filterInterface: PropTypes.arrayOf(
    PropTypes.shape({
      filter: PropTypes.string.isRequired,
      interface_type: PropTypes.string.isRequired,
      display: PropTypes.string.isRequired,
    }).isRequired).isRequired,
  fieldsLoading: PropTypes.objectOf(
    PropTypes.bool.isRequired
  ).isRequired,
};

export default connect(s => ({
  currentFilter: s.reportState.currentFilter,
  filterInterface: s.reportState.filterInterface,
  reportName: s.reportState.reportName,
  hints: s.reportState.hints,
  isValid: s.reportState.isValid,
  recordCount: s.reportState.recordCount,
  reportNameErrors: s.errors.currentErrors.name,
  intention: s.dataSetMenu.intention,
  category: s.dataSetMenu.category,
  dataSet: s.dataSetMenu.dataSet,
  reportDataId: s.dataSetMenu.reportDataId,
  fieldsLoading: s.loading.fields,
}))(SetUpReport);
