"""
XML Action Parser for LLM Agent Responses

Parses structured XML responses from AI agents with format:
<THINKING>Strategic reasoning here</THINKING>
<NEXT_ACTION>
  <PRICING><SET_PRICE>5.00</SET_PRICE></PRICING>
  <BUY_INVENTORY><SOAP>50</SOAP></BUY_INVENTORY>
  ...
</NEXT_ACTION>
"""

import re
import xml.etree.ElementTree as ET
from typing import List, Tuple, Dict, Any, Optional
from dataclasses import dataclass
from src.agents.base_agent import Action, ActionType


@dataclass
class ParsedResponse:
    """Result of parsing an LLM XML response"""
    thinking: List[str]  # All <THINKING> content blocks
    actions: List[Action]  # Parsed actions
    raw_response: str  # Original response for debugging
    parse_errors: List[str]  # Any parsing issues encountered


class XMLActionParser:
    """Parser for structured XML LLM responses"""
    
    # Mapping of XML tags to ActionType
    ACTION_MAPPING = {
        'PRICING': ActionType.SET_PRICE,
        'BUY_INVENTORY': ActionType.BUY_SUPPLIES,
        'MARKETING': ActionType.MARKETING_CAMPAIGN,
        'UPGRADE': ActionType.UPGRADE_MACHINE,
        'TICKETING': ActionType.RESOLVE_TICKET,
        'MESSAGING': ActionType.SEND_MESSAGE,
        'ALLIANCE': ActionType.PROPOSE_ALLIANCE,
        'BUYOUT': ActionType.INITIATE_BUYOUT,
        'NEGOTIATE': ActionType.NEGOTIATE,
        'WAIT': ActionType.WAIT,
        'ENDTURN': ActionType.WAIT,
    }
    
    # Inventory item mappings
    INVENTORY_ITEMS = ['SOAP', 'SOFTENER', 'PARTS', 'DETERGENT']
    
    def parse(self, response_text: str) -> ParsedResponse:
        """
        Parse an XML response from an LLM agent.
        
        Args:
            response_text: Raw XML response from LLM
            
        Returns:
            ParsedResponse with thinking, actions, and any errors
        """
        thinking = []
        actions = []
        errors = []
        
        try:
            # Extract all <THINKING> blocks
            thinking = self._extract_thinking(response_text)
            
            # Check for WAIT/ENDTURN (signals end of turn with no actions)
            if self._check_wait(response_text):
                actions.append(Action(ActionType.WAIT))
                return ParsedResponse(thinking, actions, response_text, errors)
            
            # Parse <NEXT_ACTION> block
            actions = self._parse_next_action(response_text, errors)
            
            # Default to WAIT if no actions parsed
            if not actions:
                actions.append(Action(ActionType.WAIT))
                
        except Exception as e:
            errors.append(f"Critical parse error: {str(e)}")
            actions = [Action(ActionType.WAIT)]
            
        return ParsedResponse(thinking, actions, response_text, errors)
    
    def _extract_thinking(self, text: str) -> List[str]:
        """Extract all <THINKING> blocks from response"""
        pattern = r'<THINKING>(.*?)</THINKING>'
        matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
        return [m.strip() for m in matches]
    
    def _check_wait(self, text: str) -> bool:
        """Check if response contains WAIT or ENDTURN tag"""
        wait_patterns = [
            r'<WAIT\s*/?>',
            r'<WAIT>.*?</WAIT>',
            r'<ENDTURN\s*/?>',
            r'<ENDTURN>.*?</ENDTURN>',
        ]
        for pattern in wait_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def _parse_next_action(self, text: str, errors: List[str]) -> List[Action]:
        """Parse the <NEXT_ACTION> block"""
        actions = []
        
        # Find NEXT_ACTION block
        action_match = re.search(
            r'<NEXT_ACTION>(.*?)</NEXT_ACTION>', 
            text, 
            re.DOTALL | re.IGNORECASE
        )
        
        if not action_match:
            return actions
            
        action_xml = action_match.group(1)
        
        # Wrap in root for XML parsing
        try:
            # Clean up common issues
            action_xml_clean = self._sanitize_xml(action_xml).strip()
            # print(f"DEBUG: Clean XML: {action_xml_clean}") 
            root = ET.fromstring(f"<root>{action_xml_clean}</root>")
        except ET.ParseError as e:
            errors.append(f"XML parse error: {e}")
            # Try regex fallback
            return self._regex_fallback_parse(action_xml, errors)
        
        # Parse each action type
        actions.extend(self._parse_pricing(root, errors))
        actions.extend(self._parse_inventory(root, errors))
        actions.extend(self._parse_marketing(root, errors))
        actions.extend(self._parse_upgrade(root, errors))
        actions.extend(self._parse_ticketing(root, errors))
        actions.extend(self._parse_messaging(root, errors))
        actions.extend(self._parse_alliance(root, errors))
        actions.extend(self._parse_buyout(root, errors))
        actions.extend(self._parse_negotiate(root, errors))
        
        return actions
    
    def _sanitize_xml(self, xml_text: str) -> str:
        """Clean up common XML issues from LLM output"""
        # Remove any stray text between tags
        xml_text = re.sub(r'>\s*\n\s*<', '><', xml_text)
        # Fix unclosed tags
        xml_text = re.sub(r'<([A-Z_]+)/>',  r'<\1></\1>', xml_text)
        return xml_text
    
    def _parse_pricing(self, root: ET.Element, errors: List[str]) -> List[Action]:
        """Parse <PRICING> actions"""
        actions = []
        pricing = root.find('.//PRICING')
        if pricing is None:
            pricing = root.find('.//pricing')
        
        if pricing is not None:
            # Look for SET_PRICE
            price_elem = pricing.find('.//SET_PRICE')
            if price_elem is None:
                price_elem = pricing.find('.//set_price')
            
            if price_elem is not None and price_elem.text:
                try:
                    price = float(price_elem.text.strip().replace('$', ''))
                    actions.append(Action(
                        ActionType.SET_PRICE,
                        {"price": price}
                    ))
                except ValueError:
                    errors.append(f"Invalid price value: {price_elem.text}")
        
        return actions
    
    def _parse_inventory(self, root: ET.Element, errors: List[str]) -> List[Action]:
        """Parse <BUY_INVENTORY> actions"""
        actions = []
        inventory = root.find('.//BUY_INVENTORY')
        if inventory is None:
            inventory = root.find('.//buy_inventory')
        
        if inventory is not None:
            for item in self.INVENTORY_ITEMS:
                elem = inventory.find(f'.//{item}')
                if elem is None:
                    elem = inventory.find(f'.//{item.lower()}')
                
                if elem is not None and elem.text:
                    try:
                        quantity = int(elem.text.strip())
                        if quantity > 0:
                            actions.append(Action(
                                ActionType.BUY_SUPPLIES,
                                {"item": item.lower(), "quantity": quantity}
                            ))
                    except ValueError:
                        errors.append(f"Invalid quantity for {item}: {elem.text}")
        
        return actions
    
    def _parse_marketing(self, root: ET.Element, errors: List[str]) -> List[Action]:
        """Parse <MARKETING> actions"""
        actions = []
        marketing = root.find('.//MARKETING')
        if marketing is None:
            marketing = root.find('.//marketing')
        
        if marketing is not None:
            # Look for CAMPAIGN_COST
            cost_elem = marketing.find('.//CAMPAIGN_COST')
            if cost_elem is None:
                cost_elem = marketing.find('.//campaign_cost')
            
            if cost_elem is not None and cost_elem.text:
                try:
                    cost = float(cost_elem.text.strip().replace('$', ''))
                    actions.append(Action(
                        ActionType.MARKETING_CAMPAIGN,
                        {"cost": cost}
                    ))
                except ValueError:
                    errors.append(f"Invalid marketing cost: {cost_elem.text}")
            else:
                # Default marketing cost if just <MARKETING/> or <MARKETING></MARKETING>
                actions.append(Action(
                    ActionType.MARKETING_CAMPAIGN,
                    {"cost": 100.0}  # Default cost
                ))
        
        return actions
    
    def _parse_upgrade(self, root: ET.Element, errors: List[str]) -> List[Action]:
        """Parse <UPGRADE> actions"""
        actions = []
        upgrade = root.find('.//UPGRADE')
        if upgrade is None:
            upgrade = root.find('.//upgrade')
        
        if upgrade is not None:
            # Look for MACHINES count
            machines_elem = upgrade.find('.//MACHINES')
            if machines_elem is None:
                machines_elem = upgrade.find('.//machines')
            
            count = 1  # Default to 1 machine
            if machines_elem is not None and machines_elem.text:
                try:
                    count = int(machines_elem.text.strip())
                except ValueError:
                    count = 1
            
            # Add upgrade action(s)
            for _ in range(min(count, 5)):  # Cap at 5 to prevent abuse
                actions.append(Action(ActionType.UPGRADE_MACHINE, {}))
        
        return actions
    
    def _parse_ticketing(self, root: ET.Element, errors: List[str]) -> List[Action]:
        """Parse <TICKETING> actions"""
        actions = []
        ticketing = root.find('.//TICKETING')
        if ticketing is None:
            ticketing = root.find('.//ticketing')
        
        if ticketing is not None:
            # Find all RESOLVE blocks
            for resolve in ticketing.findall('.//RESOLVE'):
                ticket_id_elem = resolve.find('.//TICKET_ID')
                if ticket_id_elem is None:
                    ticket_id_elem = resolve.find('.//ticket_id')
                
                if ticket_id_elem is not None and ticket_id_elem.text:
                    actions.append(Action(
                        ActionType.RESOLVE_TICKET,
                        {"ticket_id": ticket_id_elem.text.strip()}
                    ))
        
        return actions
    
    def _parse_messaging(self, root: ET.Element, errors: List[str]) -> List[Action]:
        """Parse <MESSAGING> actions"""
        actions = []
        messaging = root.find('.//MESSAGING')
        if messaging is None:
            messaging = root.find('.//messaging')
        
        if messaging is not None:
            # Find all MESSAGE blocks
            for msg in messaging.findall('.//MESSAGE'):
                to_elem = msg.find('.//TO')
                if to_elem is None:
                    to_elem = msg.find('.//SENDING_TO')
                if to_elem is None:
                    to_elem = msg.find('.//to')
                
                body_elem = msg.find('.//BODY')
                if body_elem is None:
                    body_elem = msg.find('.//body')
                
                if to_elem is not None and body_elem is not None:
                    if to_elem.text and body_elem.text:
                        actions.append(Action(
                            ActionType.SEND_MESSAGE,
                            {
                                "recipient_id": to_elem.text.strip(),
                                "content": body_elem.text.strip()
                            }
                        ))
        
        return actions
    
    def _parse_alliance(self, root: ET.Element, errors: List[str]) -> List[Action]:
        """Parse <ALLIANCE> actions"""
        actions = []
        alliance = root.find('.//ALLIANCE')
        if alliance is None:
            alliance = root.find('.//alliance')
        
        if alliance is not None:
            target = alliance.find('TARGET')
            if target is None:
                target = alliance.find('target')
            duration = alliance.find('DURATION')
            if duration is None:
                duration = alliance.find('duration')
            
            if target is not None and target.text:
                try:
                    dur_val = int(duration.text.strip()) if duration is not None and duration.text else 4
                    actions.append(Action(
                        ActionType.PROPOSE_ALLIANCE,
                        {"target": target.text.strip(), "duration": dur_val}
                    ))
                except ValueError:
                    errors.append("Invalid duration for alliance")
        return actions

    def _parse_buyout(self, root: ET.Element, errors: List[str]) -> List[Action]:
        """Parse <BUYOUT> actions"""
        actions = []
        buyout = root.find('.//BUYOUT')
        if buyout is None:
            buyout = root.find('.//buyout')
        
        if buyout is not None:
            target = buyout.find('TARGET')
            if target is None:
                target = buyout.find('target')
            offer = buyout.find('OFFER')
            if offer is None:
                offer = buyout.find('offer')
            
            if target is not None and target.text and offer is not None and offer.text:
                try:
                    offer_val = float(offer.text.strip().replace('$', ''))
                    actions.append(Action(
                        ActionType.INITIATE_BUYOUT,
                        {"target": target.text.strip(), "offer": offer_val}
                    ))
                except ValueError:
                    errors.append("Invalid offer for buyout")
        return actions
    
    def _parse_negotiate(self, root: ET.Element, errors: List[str]) -> List[Action]:
        """Parse <NEGOTIATE> actions"""
        actions = []
        negotiate = root.find('.//NEGOTIATE')
        if negotiate is None:
            negotiate = root.find('.//negotiate')
        
        if negotiate is not None:
            item = negotiate.find('ITEM')
            if item is None: item = negotiate.find('item')
            vendor = negotiate.find('VENDOR')
            if vendor is None: vendor = negotiate.find('vendor')
            
            if item is not None and item.text:
                vendor_id = vendor.text.strip() if vendor is not None and vendor.text else "bulkwash"
                actions.append(Action(
                    ActionType.NEGOTIATE,
                    {"item": item.text.strip(), "vendor_id": vendor_id}
                ))
        return actions

    def _regex_fallback_parse(self, text: str, errors: List[str]) -> List[Action]:
        """Fallback parsing using regex when XML parsing fails"""
        actions = []
        errors.append("Using regex fallback parser")
        
        # Try to extract price
        price_match = re.search(r'<SET_PRICE>\s*\$?([\d.]+)', text, re.IGNORECASE)
        if price_match:
            try:
                price = float(price_match.group(1))
                actions.append(Action(ActionType.SET_PRICE, {"price": price}))
            except ValueError:
                pass
        
        # Try to extract inventory purchases
        for item in self.INVENTORY_ITEMS:
            pattern = rf'<{item}>\s*(\d+)'
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    qty = int(match.group(1))
                    if qty > 0:
                        actions.append(Action(
                            ActionType.BUY_SUPPLIES,
                            {"item": item.lower(), "quantity": qty}
                        ))
                except ValueError:
                    pass
        
        # Check for marketing
        if re.search(r'<MARKETING', text, re.IGNORECASE):
            cost_match = re.search(r'<CAMPAIGN_COST>\s*\$?([\d.]+)', text, re.IGNORECASE)
            cost = 100.0
            if cost_match:
                try:
                    cost = float(cost_match.group(1))
                except ValueError:
                    pass
            actions.append(Action(ActionType.MARKETING_CAMPAIGN, {"cost": cost}))
        
        # Check for upgrade
        if re.search(r'<UPGRADE', text, re.IGNORECASE):
            actions.append(Action(ActionType.UPGRADE_MACHINE, {}))
        
        return actions


# Singleton instance for easy import
parser = XMLActionParser()


def parse_llm_response(response_text: str) -> ParsedResponse:
    """Convenience function to parse LLM response"""
    return parser.parse(response_text)
