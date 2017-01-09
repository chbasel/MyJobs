import React, {Component, PropTypes} from 'react';
import {range, map, padLeft} from 'lodash-compat';
import {Col, Row} from 'react-bootstrap';
import SelectControls from 'common/ui/SelectControls';
import {monthsArray} from 'common/calendar-support';

export default class DateTimePicker extends Component {
  componentWillMount() {
    const {value, onChange} = this.props;
    // default state is loaded regardless so that we have yearRangeMin/Max
    this.state = this.getDefaultState();
    if (value) this.stringToState(value);
    else onChange({target: {value: this.stateToString()}});
  }

  componentWillReceiveProps(newProps) {
    const {value} = newProps;
    if (value) this.stringToState(value);
  }

  getDefaultState() {
    const today = new Date();
    return {
      selectMonth: today.getMonth() + 1,
      selectDay: today.getDate(),
      selectYear: +today.getFullYear(),
      selectHour: this.resolveHours(today.getHours()),
      selectAMPM: this.resolveAMPM(today.getHours()),
      selectMinute: today.getMinutes(),
      yearRangeMax: today.getFullYear() + 2,
      yearRangeMin: today.getFullYear() - 20,
    };
  }

  resolveHours(hours) {
    return ((h) => (+h > 12 ? +h - 12 : h))(hours);
  }

  resolveAMPM(hours) {
    return ((h) => (+h >= 12 ? 1 : 0))(hours);
  }

  backToMilitaryTime(hours, AMPM) {
    if (+hours === 12) {
      if (+AMPM) {
        return 12;
      }
      return 0;
    }
    return (+AMPM ? +hours + 12 : +hours);
  }

  rangeToDropDownArray(rangeStart, rangeEnd) {
    return map(range(rangeStart, rangeEnd),
      (n) => ({value: n, display: padLeft(n, 2, '0'), render: () => ''}));
  }

  stringToState(input) {
    const re = /^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2})/i;
    const matchValues = re.exec(input);
    this.setState({
      selectYear: +matchValues[1],
      selectMonth: +matchValues[2],
      selectDay: +matchValues[3],
      selectHour: +this.resolveHours(matchValues[4]),
      selectAMPM: +this.resolveAMPM(matchValues[4]),
      selectMinute: +matchValues[5],
    });
  }

  handleFieldChange(field, value) {
    const {onChange} = this.props;
    this.setState({
      [field]: value,
    }, () => onChange({target: {value: this.stateToString()}}));
  }

  stateToString() {
    const {selectYear, selectHour, selectAMPM} = this.state;
    const padMonth = padLeft(this.state.selectMonth, 2, '0');
    const padDay = padLeft(this.state.selectDay, 2, '0');
    const padMinute = padLeft(this.state.selectMinute, 2, '0');
    const convertPadHour = padLeft(
      this.backToMilitaryTime(selectHour, selectAMPM), 2, '0'
    );
    return selectYear + '-' + padMonth + '-' + padDay + ' ' +
      convertPadHour + ':' + padMinute;
  }

  render() {
    const {selectYear, selectMonth, selectDay,
      selectHour, selectMinute, yearRangeMin, yearRangeMax, selectAMPM} = this.state;

    return (
      <div>
        <Row>
          <Col xs={4} md={4}>
            <SelectControls
              choices={map(monthsArray, (a) => ({...a, render: () => ''}))}
              value={selectMonth}
              onSelect={v => this.handleFieldChange('selectMonth', v)}/>
          </Col>
          <Col xs={4} md={4}>
            <SelectControls
              choices={this.rangeToDropDownArray(1, 32)}
              value={selectDay}
              onSelect={v => this.handleFieldChange('selectDay', v)}/>
          </Col>
          <Col xs={4} md={4}>
            <SelectControls
              choices={this.rangeToDropDownArray(yearRangeMin, yearRangeMax)}
              value={selectYear}
              onSelect={v => this.handleFieldChange('selectYear', v)}/>
          </Col>
        </Row>
        <Row>
          <Col xs={4} md={4}>
            <SelectControls
              choices={this.rangeToDropDownArray(1, 13)}
              value={selectHour}
              onSelect={v => this.handleFieldChange('selectHour', v)}/>
          </Col>
          <Col xs={4} md={4}>
            <SelectControls
              choices={this.rangeToDropDownArray(0, 60)}
              value={selectMinute}
              onSelect={v => this.handleFieldChange('selectMinute', v)}/>
          </Col>
          <Col xs={4} md={4}>
            <SelectControls
              choices={[
                {value: 0, display: 'AM', render: () => ''},
                {value: 1, display: 'PM', render: () => ''},
              ]}
              value={selectAMPM}
              onSelect={v => this.handleFieldChange('selectAMPM', v)}/>
          </Col>
        </Row>
      </div>
    );
  }
}

DateTimePicker.defaultProps = {
  value: '',
};

DateTimePicker.propTypes = {
  /**
   * what to do when a field changes
   */
  onChange: PropTypes.func.isRequired,

  /**
   * value from the data store in regex parseable string
   * format: YYYY-MM-DD HH:MM
   */
  value: PropTypes.string,
};
