from typing import Any

import frappe


def _get_or_set(name: str, getter: callable, expires_in_sec: int | None = 60 * 60) -> Any | None:
	"""Get or set a value in the cache."""

	value = frappe.cache.get_value(name)

	if not value:
		value = getter()
		frappe.cache.set_value(name, value, expires_in_sec=expires_in_sec)

	if isinstance(value, bytes):
		value = value.decode()

	return value


def _hget_or_hset(name: str, key: str, getter: callable) -> Any | None:
	"""Get or set a value in the cache hash."""

	value = frappe.cache.hget(name, key)

	if not value:
		value = getter()
		frappe.cache.hset(name, key, value)

	return value


def delete_cache(name: str, key: str | None = None) -> None:
	"""Delete a value from the cache."""

	if not key:
		frappe.cache.delete_value(name)
	else:
		frappe.cache.hdel(name, key)


def get_root_domain_name() -> str | None:
	"""Returns the root domain name."""

	def getter() -> str | None:
		return frappe.db.get_single_value("Mail Server Settings", "root_domain_name")

	return _get_or_set("root_domain_name", getter, expires_in_sec=None)


def get_blacklist_for_ip_group(ip_group: str) -> list:
	"""Returns the blacklist for the IP group."""

	def getter() -> list:
		IP_BLACKLIST = frappe.qb.DocType("IP Blacklist")
		return (
			frappe.qb.from_(IP_BLACKLIST)
			.select(
				IP_BLACKLIST.name,
				IP_BLACKLIST.is_blacklisted,
				IP_BLACKLIST.ip_address,
				IP_BLACKLIST.ip_address_expanded,
				IP_BLACKLIST.blacklist_reason,
			)
			.where(IP_BLACKLIST.ip_group == ip_group)
		).run(as_dict=True)

	return _get_or_set(f"blacklist|{ip_group}", getter, expires_in_sec=24 * 60 * 60)
