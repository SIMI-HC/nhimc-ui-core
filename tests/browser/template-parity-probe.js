export function summarizeTemplateCell(observation) {
  return {
    structure: JSON.stringify(observation.canonicalRoles) ===
      JSON.stringify(observation.artifactRoles) &&
      observation.requiredComponentsPresent === true,
    responsive: observation.documentOverflow === false,
    focus: Number.isInteger(observation.focusableCount) &&
      observation.focusableCount === observation.canonicalFocusableCount,
    pixels: observation.screenshotBytes > 0,
    frameIsolation: observation.frameGeometryStable === true,
  };
}
