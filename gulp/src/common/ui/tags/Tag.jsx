import React, {PropTypes} from 'react';
import classnames from 'classnames';
import tinycolor from 'tinycolor2';


/**
 * Show a single tag.
 */
export function Tag(props) {
  const {
    display,
    hexColor,
    onRemoveTag,
    onClick,
    onMouseEnter,
    onMouseLeave,
    highlight,
  } = props;

  let backgroundColor;
  let borderColor;
  if (highlight) {
    backgroundColor = tinycolor(hexColor)
      .lighten(10).toHexString();
    borderColor = tinycolor(hexColor)
      .lighten(5).toHexString();
  } else {
    backgroundColor = '#' + hexColor;
    borderColor = tinycolor(hexColor)
      .darken(10).toHexString();
  }
  const textColor =
    tinycolor.mostReadable(backgroundColor, ['#000', '#fff']).toHexString();

  return (
    <span
      className={
        classnames(
          'tag-select-tag',
          {'higlighted': highlight},
          {'removable': onRemoveTag})}
      style={{backgroundColor, borderColor, color: textColor}}
      onClick={e => {e.stopPropagation(); onClick(e);}}
      onMouseEnter={(e) => onMouseEnter(e)}
      onMouseLeave={(e) => onMouseLeave(e)}>
      {display}
      {onRemoveTag ? <i onClick={e => {e.stopPropagation(); onRemoveTag();}}/> : ''}
    </span>
  );
}

Tag.defaultProps = {
  hexColor: 'dddddd',
};

Tag.propTypes = {
  /**
   * Display name for this tag.
   */
  display: PropTypes.string.isRequired,

  /**
   * Color to use for this tag.
   */
  hexColor: PropTypes.string,

  /**
   * Is this tag currently highlighted?
   */
  highlight: PropTypes.bool,

  /**
   * Callback: call with no args to indicate that the user clicked remove.
   *
   * Optional: If not present, no UI for tags removal will appear.
   */
  onRemoveTag: PropTypes.func,

  /**
   * Callback: user clicked the tag
   */
  onClick: PropTypes.func.isRequired,

  /**
   * Callback: mouse hovered over the tag
   */
  onMouseEnter: React.PropTypes.func,

  /**
   * Callback: mouse left the tag
   */
  onMouseLeave: React.PropTypes.func,
};
