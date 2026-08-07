export function navigate(pathname: "/" | "/analisar" | "/relatorio"): void {
  window.history.pushState(null, "", pathname);
  window.dispatchEvent(new PopStateEvent("popstate"));
}
