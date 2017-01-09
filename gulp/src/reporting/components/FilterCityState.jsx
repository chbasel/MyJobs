import React, {PropTypes, Component} from 'react';
import Select from 'common/ui/Select';
import {SearchInput} from 'common/ui/SearchInput';
import {getDisplayForValue} from 'common/array';


export default class FilterCityState extends Component {
  updateField(field, value) {
    const {updateFilter, values} = this.props;

    const newValues = {
      ...values,
      [field]: value,
    };
    updateFilter(newValues);
  }

  render() {
    const {
      id,
      getHints,
      hints,
      values,
      stateLoading,
      cityLoading,
    } = this.props;
    const stateValue = values.state || '';

    const stateHints = hints.state || [];
    const cityValue = values.city || '';

    const regionsWithBlank = [
      {
        display: 'Select a State',
        value: '',
      },
      ...stateHints,
    ];

    return (
      <span>
        <Select
          onChange={e =>
            this.updateField('state', e.target.value)}
          name=""
          value={getDisplayForValue(regionsWithBlank, stateValue)}
          choices={regionsWithBlank}
          disable={stateLoading}
        />
        <SearchInput
          id={id + '-city'}
          value={cityValue}
          callSelectWhenEmpty
          placeholder="city"
          onSelect={v =>
            this.updateField('city', v.value)}
          getHints={v =>
            getHints('city', v)}
          loading={cityLoading}
          hints={hints.city}
        />
      </span>
    );
  }
}

FilterCityState.propTypes = {
  // unique id to use for this React component
  id: PropTypes.string.isRequired,
  // values to display
  values: PropTypes.shape({
    city: PropTypes.string,
    state: PropTypes.string,
  }).isRequired,
  updateFilter: PropTypes.func.isRequired,
  // callback used to get valid optoins for cities and regions
  getHints: PropTypes.func.isRequired,
  // known hints
  hints: PropTypes.object,
  stateLoading: PropTypes.bool,
  cityLoading: PropTypes.bool,
};
