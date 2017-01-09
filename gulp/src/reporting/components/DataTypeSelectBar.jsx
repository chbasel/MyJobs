import React, {Component, PropTypes} from 'react';
import Select from 'common/ui/Select';
import {getDisplayForValue} from 'common/array';
import {connect} from 'react-redux';

class DataTypeSelectBar extends Component {
  render() {
    const {
      intentionChoices,
      intentionValue,
      onIntentionChange,
      categoryChoices,
      categoryValue,
      onCategoryChange,
      dataSetChoices,
      dataSetValue,
      onDataSetChange,
    } = this.props;

    return (
      <div className="row">
        <fieldset className="fieldset-border">
            <legend className="fieldset-border">Report Configuration</legend>
            <div className="col-xs-3">
              <label>Report Intention</label>
              <Select
                onChange={e => onIntentionChange(e.target.value, e.target.obj)}
                choices = {intentionChoices}
                value = {
                  getDisplayForValue(intentionChoices, intentionValue)}
                name = ""
              />
            </div>
            <div className="col-xs-3">
              <label>Report Category</label>
              <Select
                onChange={e => onCategoryChange(e.target.value)}
                choices = {categoryChoices}
                value = {
                  getDisplayForValue(categoryChoices, categoryValue)}
                name = ""
              />
            </div>
            <div className="col-xs-6">
              <label>Data Set</label>
              <Select
                onChange={e => onDataSetChange(e.target.value)}
                choices = {dataSetChoices}
                value = {
                  getDisplayForValue(dataSetChoices, dataSetValue)}
                name = ""
              />
            </div>
        </fieldset>
      </div>
    );
  }
}

DataTypeSelectBar.propTypes = {
  intentionChoices: PropTypes.arrayOf(
    PropTypes.shape({
      value: PropTypes.any.isRequired,
      display: PropTypes.string.isRequired,
    })
  ),
  intentionValue: PropTypes.string.isRequired,
  onIntentionChange: PropTypes.func.isRequired,

  categoryChoices: PropTypes.arrayOf(
    PropTypes.shape({
      value: PropTypes.any.isRequired,
      display: PropTypes.string.isRequired,
    })
  ),
  categoryValue: PropTypes.string.isRequired,
  onCategoryChange: PropTypes.func.isRequired,
  dataSetChoices: PropTypes.arrayOf(
    PropTypes.shape({
      value: PropTypes.any.isRequired,
      display: PropTypes.string.isRequired,
    })
  ),
  dataSetValue: PropTypes.string.isRequired,
  onDataSetChange: PropTypes.func.isRequired,
};

export default connect(s => s.dataSetMenu || {})(DataTypeSelectBar);
