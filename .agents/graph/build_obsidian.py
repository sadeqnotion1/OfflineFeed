#!/usr/bin/env python3
"""
build_obsidian.py -- Convert graph.json into an Obsidian vault.

Creates markdown notes for each node, organized into folders by community,
and links them using Obsidian [[WikiLinks]] based on graph edges.
Also generates a nice Welcome.md dashboard.
"""

import json
import re
import shutil
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
GRAPH_JSON = HERE / "graph.json"
VAULT_DIR = HERE / "Offlinefeed"

def sanitize_filename(name: str) -> str:
    """Replace Windows-forbidden characters and spaces with a single underscore."""
    # Forbidden in Windows filenames: \ / : * ? " < > |
    sanitized = re.sub(r'[\\/:*?"<>|\s]+', '_', name)
    sanitized = re.sub(r'_+', '_', sanitized)
    sanitized = sanitized.strip('_')
    if not sanitized:
        sanitized = "empty_id"
    return sanitized

def clean_vault_except_config():
    """Remove previously generated community folders and markdown files, preserving .obsidian config."""
    if not VAULT_DIR.exists():
        return
        
    for item in VAULT_DIR.iterdir():
        if item.is_dir():
            # Keep Obsidian config directory
            if item.name == ".obsidian":
                continue
            # Remove other folders (which should be communities)
            try:
                shutil.rmtree(item)
            except Exception as e:
                print(f"Warning: Could not remove directory {item}: {e}")
        elif item.is_file():
            # Keep Welcome.md if we want to overwrite it cleanly, but delete it if we regenerate
            if item.name.lower() == "welcome.md":
                item.unlink(missing_ok=True)
            elif item.suffix.lower() == ".md":
                item.unlink(missing_ok=True)

def main():
    if not GRAPH_JSON.exists():
        print(f"Error: graph.json not found at {GRAPH_JSON}")
        sys.exit(1)
        
    try:
        graph = json.loads(GRAPH_JSON.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"Error parsing graph.json: {e}")
        sys.exit(1)

    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])
    meta = graph.get("meta", {})
    
    print(f"Loaded graph: {len(nodes)} nodes, {len(edges)} edges.")
    
    # 1. Clean previous run
    clean_vault_except_config()
    VAULT_DIR.mkdir(parents=True, exist_ok=True)
    
    # 2. Map node IDs to sanitized unique filenames (without extension)
    id_to_filename = {}
    used_filenames = set()
    
    for n in nodes:
        node_id = n.get("id")
        if not node_id:
            continue
        base = sanitize_filename(node_id)
        candidate = base
        counter = 1
        while candidate.lower() in used_filenames:
            candidate = f"{base}_{counter}"
            counter += 1
        used_filenames.add(candidate.lower())
        id_to_filename[node_id] = candidate

    # 3. Build outgoing and incoming maps for edges
    outgoing = {n.get("id"): [] for n in nodes if n.get("id")}
    incoming = {n.get("id"): [] for n in nodes if n.get("id")}
    
    for e in edges:
        s = e.get("source", e.get("from"))
        t = e.get("target", e.get("to"))
        if not s or not t:
            continue
        # Ensure keys exist (handle potentially dangling edges gracefully)
        if s not in outgoing:
            outgoing[s] = []
        if t not in incoming:
            incoming[t] = []
        outgoing[s].append(e)
        incoming[t].append(e)

    # 4. Generate markdown file for each node
    for n in nodes:
        node_id = n.get("id")
        if not node_id or node_id not in id_to_filename:
            continue
            
        filename = id_to_filename[node_id]
        community = n.get("community") or n.get("layer") or "other"
        
        # Sanitize community name for folder structure
        community_folder_name = sanitize_filename(community)
        community_dir = VAULT_DIR / community_folder_name
        community_dir.mkdir(parents=True, exist_ok=True)
        
        filepath = community_dir / f"{filename}.md"
        
        label = n.get("label", node_id)
        node_type = n.get("type", "unknown")
        location = n.get("location", "")
        degree = n.get("degree", 0)
        summary = n.get("summary") or n.get("desc") or ""
        
        # Format markdown content with Frontmatter metadata
        lines = []
        lines.append("---")
        lines.append(f"id: \"{node_id}\"")
        lines.append(f"label: \"{label}\"")
        lines.append(f"type: \"{node_type}\"")
        lines.append(f"community: \"{community}\"")
        if location:
            lines.append(f"location: \"{location}\"")
        lines.append(f"degree: {degree}")
        lines.append("---")
        lines.append("")
        lines.append(f"# {label}")
        lines.append("")
        lines.append(f"- **Type**: `{node_type}`")
        lines.append(f"- **Community**: `{community}`")
        if location:
            # Let's make location clickable if it references a file
            # Format is usually: filename.py:line
            file_part = location.split(":")[0] if ":" in location else location
            lines.append(f"- **Location**: `{location}`")
        lines.append(f"- **Degree**: `{degree}`")
        lines.append("")
        lines.append("## Summary")
        if summary:
            lines.append(summary)
        else:
            lines.append("*No summary available.*")
        lines.append("")
        
        # Outgoing connections
        lines.append("## Outgoing Connections")
        out_edges = outgoing.get(node_id, [])
        if out_edges:
            for oe in out_edges:
                target_id = oe.get("target", oe.get("to"))
                edge_type = oe.get("type", "references")
                evidence = oe.get("evidence", "")
                
                target_node = next((node for node in nodes if node.get("id") == target_id), None)
                target_label = target_node.get("label", target_id) if target_node else target_id
                
                if target_id in id_to_filename:
                    target_file = id_to_filename[target_id]
                    link = f"[[{target_file}|{target_label}]]"
                else:
                    link = f"`{target_label}` (external)"
                
                evidence_str = f" (*evidence: {evidence}*)" if evidence else ""
                lines.append(f"- {link} (type: `{edge_type}`{evidence_str})")
        else:
            lines.append("*None*")
        lines.append("")
        
        # Incoming connections
        lines.append("## Incoming Connections")
        in_edges = incoming.get(node_id, [])
        if in_edges:
            for ie in in_edges:
                source_id = ie.get("source", ie.get("from"))
                edge_type = ie.get("type", "references")
                evidence = ie.get("evidence", "")
                
                source_node = next((node for node in nodes if node.get("id") == source_id), None)
                source_label = source_node.get("label", source_id) if source_node else source_id
                
                if source_id in id_to_filename:
                    source_file = id_to_filename[source_id]
                    link = f"[[{source_file}|{source_label}]]"
                else:
                    link = f"`{source_label}` (external)"
                
                evidence_str = f" (*evidence: {evidence}*)" if evidence else ""
                lines.append(f"- {link} (type: `{edge_type}`{evidence_str})")
        else:
            lines.append("*None*")
            
        filepath.write_text("\n".join(lines), encoding="utf-8")
        
    # 5. Generate Welcome.md dashboard
    # Group nodes by community for the index
    communities_nodes = {}
    for n in nodes:
        node_id = n.get("id")
        if not node_id or node_id not in id_to_filename:
            continue
        community = n.get("community") or n.get("layer") or "other"
        communities_nodes.setdefault(community, []).append(n)
        
    # Find God nodes (highest degree)
    sorted_nodes_by_degree = sorted(
        [n for n in nodes if n.get("id") in id_to_filename],
        key=lambda x: x.get("degree", 0),
        reverse=True
    )
    god_nodes = sorted_nodes_by_degree[:8]
    
    welcome_lines = [
        "# OfflineFeed Knowledge Graph Vault",
        "",
        "Welcome to the Obsidian representation of the OfflineFeed codebase knowledge graph.",
        "",
        "## Vault Stats",
        f"- **Total Nodes/Notes**: {len(nodes)}",
        f"- **Total Connections/Edges**: {len(edges)}",
        f"- **Project Repo**: [{meta.get('repo', 'sadeqnotion1/OfflineFeed')}](https://github.com/{meta.get('repo', 'sadeqnotion1/OfflineFeed')})",
        f"- **Generated At**: {meta.get('generated', 'N/A')}",
        "",
        "---",
        "",
        "## Key God Nodes (Most Connected)",
        "These are the central hubs of the codebase. Start exploring here:",
    ]
    
    for gn in god_nodes:
        gn_id = gn.get("id")
        gn_file = id_to_filename[gn_id]
        gn_label = gn.get("label", gn_id)
        gn_type = gn.get("type", "unknown")
        gn_degree = gn.get("degree", 0)
        gn_desc = gn.get("summary") or gn.get("desc") or ""
        # Keep description short for the dashboard
        gn_desc_short = gn_desc[:120] + "..." if len(gn_desc) > 120 else gn_desc
        welcome_lines.append(f"- [[{gn_file}|{gn_label}]] (`{gn_type}`, degree: {gn_degree}) — {gn_desc_short}")
        
    welcome_lines.extend([
        "",
        "---",
        "",
        "## Folders & Communities",
        "The codebase has been divided into the following functional areas:",
    ])
    
    for comm in sorted(communities_nodes.keys()):
        comm_nodes = communities_nodes[comm]
        comm_folder = sanitize_filename(comm)
        welcome_lines.append(f"### [[{comm_folder}/|{comm.title()}]] ({len(comm_nodes)} nodes)")
        # Show top 5 nodes for each community as quick links
        sorted_comm_nodes = sorted(comm_nodes, key=lambda x: x.get("degree", 0), reverse=True)[:5]
        links = []
        for cn in sorted_comm_nodes:
            cn_id = cn.get("id")
            cn_file = id_to_filename[cn_id]
            cn_label = cn.get("label", cn_id)
            links.append(f"[[{cn_file}|{cn_label}]]")
        welcome_lines.append("  " + " · ".join(links))
        
    welcome_lines.extend([
        "",
        "---",
        "",
        "## Tips for Using this Vault in Obsidian",
        "1. **Graph View**: Open the built-in Graph View in Obsidian (`Ctrl+G`) to see the interactive visual representation of your codebase.",
        "2. **Backlinks**: Toggle the Backlinks pane in Obsidian to see what calls or references the note you are currently viewing.",
        "3. **Frontmatter Search**: You can search notes by metadata, e.g., `type:file` or `community:backend`.",
    ])
    
    welcome_file = VAULT_DIR / "Welcome.md"
    welcome_file.write_text("\n".join(welcome_lines), encoding="utf-8")
    
    print(f"Generated Welcome.md dashboard at {welcome_file}")
    print("Obsidian system generation complete!")

if __name__ == "__main__":
    main()
